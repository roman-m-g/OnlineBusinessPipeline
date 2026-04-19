from airflow.sdk import dag, task
from airflow.providers.standard.operators.empty import EmptyOperator
import pendulum


@dag(
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    tags=['currency', 'online_business'],
)
def gbp_monthly_avg_to_gcs():

    @task
    def fetch_and_upload_monthly_avg() -> None:
        import requests
        import csv
        import io
        from collections import defaultdict
        from airflow.providers.google.cloud.hooks.gcs import GCSHook

        # Frankfurter supports date ranges: /v1/{start}..{end}
        # Returns daily rates — we aggregate to monthly averages
        response = requests.get(
            'https://api.frankfurter.dev/v1/2010-01-01..',
            params={'base': 'GBP', 'symbols': 'USD,EUR'},
        )
        response.raise_for_status()
        data = response.json()

        # Aggregate daily rates into monthly buckets
        # data['rates'] = {'2010-01-04': {'USD': 1.61, 'EUR': 1.13}, ...}
        monthly = defaultdict(lambda: defaultdict(list))
        for date_str, rates in data['rates'].items():
            year_month = date_str[:7]  # 'YYYY-MM'
            for currency, rate in rates.items():
                monthly[year_month][currency].append(rate)

        # Build CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['year_month', 'avg_rate_gpb_usd', 'avg_rate_gpb_eur'])

        for year_month in sorted(monthly.keys()):
            rates_by_currency = monthly[year_month]
            usd_rates = rates_by_currency.get('USD', [])
            eur_rates = rates_by_currency.get('EUR', [])
            writer.writerow([
                year_month,
                round(sum(usd_rates) / len(usd_rates), 6) if usd_rates else '',
                round(sum(eur_rates) / len(eur_rates), 6) if eur_rates else '',
            ])

        hook = GCSHook(gcp_conn_id='gcp')
        hook.upload(
            bucket_name='obp-486617',
            object_name='raw/currency_rates/gbp_monthly_avg_2010_2026.csv',
            data=output.getvalue(),
            mime_type='text/csv',
        )

    start = EmptyOperator(task_id='start')
    finish = EmptyOperator(task_id='finish')

    start >> fetch_and_upload_monthly_avg() >> finish


gbp_monthly_avg_to_gcs()
