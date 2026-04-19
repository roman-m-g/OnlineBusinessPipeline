from airflow.sdk import dag, task
from airflow.providers.standard.operators.empty import EmptyOperator
import pendulum

from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook

from include.dbt.cosmos_config import DBT_PROJECT_CONFIG, DBT_CONFIG
from cosmos.airflow.task_group import DbtTaskGroup
from cosmos.constants import LoadMode, InvocationMode
from cosmos.config import RenderConfig, ExecutionConfig


@dag(
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    tags=['online_business'],
)
def online_business():

    @task
    def upload_online_business_to_gcs() -> None:
        hook = GCSHook(gcp_conn_id='gcp')
        hook.upload(
            bucket_name='obp-486617',
            object_name='raw/online_business.csv',
            filename='include/dataset/online_business.csv',
            mime_type='text/csv',
        )

    @task
    def upload_currency_rates_to_gcs() -> None:
        hook = GCSHook(gcp_conn_id='gcp')
        hook.upload(
            bucket_name='obp-486617',
            object_name='raw/currencyrates.csv',
            filename='include/dataset/currency_rates_gbp_monthly_avg_2010-2026.csv',
            mime_type='text/csv',
        )

    # @task
    # def create_online_business_dataset() -> None:
    #     hook = BigQueryHook(gcp_conn_id='gcp')
    #     hook.create_empty_dataset(
    #         dataset_id='online_business',
    #         location='EU',
    #         exists_ok=True,
    #     )

    @task
    def gcs_online_business_to_bq_raw() -> None:
        hook = BigQueryHook(gcp_conn_id='gcp')
        job_config = {
            'load': {
                'destinationTable': {
                    'projectId': hook.project_id,
                    'datasetId': 'online_business',
                    'tableId': 'raw_invoices',
                },
                'sourceUris': ['gs://obp-486617/raw/online_business.csv'],
                'sourceFormat': 'CSV',
                'skipLeadingRows': 1,
                'writeDisposition': 'WRITE_TRUNCATE',
                'allowQuotedNewlines': True,
                'allowJaggedRows': True,
                'encoding': 'UTF-8',
                'schema': {
                    'fields': [
                        {'name': 'InvoiceNo',    'type': 'STRING',  'mode': 'NULLABLE'},
                        {'name': 'StockCode',    'type': 'STRING',  'mode': 'NULLABLE'},
                        {'name': 'Description',  'type': 'STRING',  'mode': 'NULLABLE'},
                        {'name': 'Quantity',     'type': 'INTEGER', 'mode': 'NULLABLE'},
                        {'name': 'InvoiceDate',  'type': 'STRING',  'mode': 'NULLABLE'},
                        {'name': 'UnitPrice',    'type': 'FLOAT',   'mode': 'NULLABLE'},
                        {'name': 'CustomerID',   'type': 'FLOAT',   'mode': 'NULLABLE'},
                        {'name': 'Country',      'type': 'STRING',  'mode': 'NULLABLE'},
                    ]
                },
            }
        }
        hook.insert_job(configuration=job_config)

    @task
    def gcs_currency_rates_to_bq_raw() -> None:
        hook = BigQueryHook(gcp_conn_id='gcp')
        job_config = {
            'load': {
                'destinationTable': {
                    'projectId': hook.project_id,
                    'datasetId': 'online_business',
                    'tableId': 'raw_currency_rates',
                },
                'sourceUris': ['gs://obp-486617/raw/currencyrates.csv'],
                'sourceFormat': 'CSV',
                'skipLeadingRows': 1,
                'writeDisposition': 'WRITE_TRUNCATE',
                'encoding': 'UTF-8',
                'schema': {
                    'fields': [
                        {'name': 'year_month',       'type': 'STRING', 'mode': 'NULLABLE'},
                        {'name': 'avg_rate_gpb_usd', 'type': 'FLOAT',  'mode': 'NULLABLE'},
                        {'name': 'avg_rate_gpb_eur', 'type': 'FLOAT',  'mode': 'NULLABLE'},
                    ]
                },
            }
        }
        hook.insert_job(configuration=job_config)

    @task.external_python(python='/usr/local/airflow/soda_venv/bin/python')
    def check_load(scan_name='check_load', checks_subpath='sources'):
        from include.soda.check_function import check
        return check(scan_name, checks_subpath, data_source='online_business')

    transform = DbtTaskGroup(
        group_id='transform',
        project_config=DBT_PROJECT_CONFIG,
        profile_config=DBT_CONFIG,
        render_config=RenderConfig(
            load_method=LoadMode.DBT_LS,
            select=['path:models/transform'],
        ),
        execution_config=ExecutionConfig(
            invocation_mode=InvocationMode.SUBPROCESS,
            dbt_executable_path='/usr/local/airflow/dbt_venv/bin/dbt',
        ),
    )



    @task.external_python(python='/usr/local/airflow/soda_venv/bin/python')
    def check_transform(scan_name='check_transform', checks_subpath='transform'):
        from include.soda.check_function import check
        return check(scan_name, checks_subpath, data_source='online_business')


    report = DbtTaskGroup(
        group_id='report',
        project_config=DBT_PROJECT_CONFIG,
        profile_config=DBT_CONFIG,
        render_config=RenderConfig(
            load_method=LoadMode.DBT_LS,
            select=['path:models/report'],
        ),
        execution_config=ExecutionConfig(
            invocation_mode=InvocationMode.SUBPROCESS,
            dbt_executable_path='/usr/local/airflow/dbt_venv/bin/dbt',
        ),
    )

    @task.external_python(python='/usr/local/airflow/soda_venv/bin/python')
    def check_report(scan_name='check_report', checks_subpath='report'):
        from include.soda.check_function import check

        return check(scan_name, checks_subpath, data_source='online_business')

    start = EmptyOperator(task_id='start')
    finish = EmptyOperator(task_id='finish')

    upload_ob = upload_online_business_to_gcs()
    upload_cr = upload_currency_rates_to_gcs()
    raw_ob = gcs_online_business_to_bq_raw()
    raw_cr = gcs_currency_rates_to_bq_raw()
    check = check_load()

    start >> [upload_ob, upload_cr]
    upload_ob >> raw_ob
    upload_cr >> raw_cr
    [raw_ob, raw_cr] >> check >> transform >> check_transform() >> report >> check_report() >> finish


online_business()
