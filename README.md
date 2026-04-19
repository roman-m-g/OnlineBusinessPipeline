# Online Business Pipeline

An online business operates across multiple countries and accumulates transactional invoice data in flat CSV files. The business has no centralised analytics capability — data is siloed, unvalidated, and unavailable for reporting. The goal of this project is to build an end-to-end data pipeline that ingests raw business data, connect with currency rates, then transforms it into a dimensional model, validates data quality at each stage, and makes it available for business intelligence reporting in Google Data Studio.


## Architecture

The pipeline follows an **ELT** pattern: raw data is landed in a cloud data lake first, then loaded into the data warehouse, and transformed in-place using dbt. Data quality checks run at each stage before the next begins.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Local Source Files                           │
│   online_business.csv   country.csv   currency_rates_gbp.csv        │
└────────────────────────────┬────────────────────────────────────────┘
                             │  
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  Google Cloud Storage (Data Lake)                   │
│            gs://obp-486617/raw/  *.csv                              │
└────────────────────────────┬────────────────────────────────────────┘
                             │  
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│              BigQuery — Raw Layer  (online_business dataset)        │
│        raw_invoices     raw_currency_rates     country              │
└──────────────┬──────────────────────────────────────────────────────┘
               │  Soda Core: checks/sources
               ▼
          ┌─────────┐  pass
          │  check  ├──────────────────────────────────────────────┐
          │  load   │                                              │
          └────┬────┘                                              │
               │ fail → DAG stops                                  │
                                                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│           BigQuery — Transform Layer  (dbt + Cosmos)                │
│   dim_customers  dim_product  dim_datetime  dim_currency_rates      │
│   fct_invoices                                                      │
└──────────────┬──────────────────────────────────────────────────────┘
               │  Soda Core: checks/transform
               ▼
          ┌─────────┐  pass
          │  check  ├──────────────────────────────────────────────┐
          │transform│                                              │
          └────┬────┘                                              │
               │ fail → DAG stops                                  │
                                                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│             BigQuery — Report Layer  (dbt + Cosmos)                 │
│  report_country_revenue   report_customer_segments                  │
│  report_monthly_revenue   report_product_performance                │
│  report_product_invoices                                            │
└──────────────┬──────────────────────────────────────────────────────┘
               │  Soda Core: checks/report
               ▼
          ┌─────────┐  pass
          │  check  ├──────────────────────────────────────────────┐
          │ report  │                                              │
          └─────────┘                                              │
                                                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Google Data Studio                               │
│           Dashboards connected directly to BigQuery                 │
└─────────────────────────────────────────────────────────────────────┘
```




### Airflow DAG Flow

#### Currency rates GBP to USD & EUR 2010-2026 Dag

![CurrencyRates](pics/CurrencyRates2010_2026.png)

###  Online Business Pipeline Dag

![OnlineBusinessPipelineDag](pics/OnlineBusinessPipelineDag.png)


## Tech Stack


| Layer | Tool | Location |
|---|---|---|
| Orchestration | Apache Airflow 3.x (Astronomer Runtime) | Docker / Astro CLI |
| Infrastructure | Terraform | GCS bucket + BigQuery dataset |
| Data Lake | Google Cloud Storage | `gs://obp-486617/raw/` |
| Raw Load | BigQuery Load Jobs via `BigQueryHook` | `online_business.*_raw` tables |
| Data Quality | Soda Core (`soda-core-bigquery`) | `include/soda/checks/` |
| Transform | dbt Core 1.11 + Cosmos (`dbt-bigquery`) | `include/dbt/models/transform/` |
| Report Models | dbt Core 1.11 + Cosmos | `include/dbt/models/report/` |
| Visualisation | Google Data Studio | Connected to BigQuery report layer |



## Project Structure

```
OnlineBusinessPipeline/
│
├── dags/
│   ├── online_business.py          
│   └── gbp_monthly_avg_to_gcs.py   
│
├── include/
│   ├── dataset/                   
│   │   ├── online_business.csv
│   │   ├── country.csv
│   │   └── raw_currency_rates_gbp_monthly_avg_2010_2026.csv
│   │
│   ├── dbt/                        
│   │   ├── models/
│   │   │   ├── sources/
│   │   │   │   └── sources.yml     
│   │   │   ├── transform/          
│   │   │   │   ├── dim_customers.sql
│   │   │   │   ├── dim_product.sql
│   │   │   │   ├── dim_datetime.sql
│   │   │   │   ├── dim_currency_rates.sql
│   │   │   │   └── fct_invoices.sql
│   │   │   └── report/             
│   │   │       ├── report_country_revenue.sql
│   │   │       ├── report_customer_segments.sql
│   │   │       ├── report_monthly_revenue.sql
│   │   │       ├── report_product_invoices.sql
│   │   │       └── report_product_performance.sql
│   │   ├── cosmos_config.py        
│   │   ├── dbt_project.yml
│   │   ├── profiles.yml            
│   │   └── packages.yml            
│   │
│   ├── soda/                       
│   │   ├── check_function.py       
│   │   ├── configuration.yml       
│   │   └── checks/
│   │       ├── sources/           
│   │       │   ├── raw_invoices.yml
│   │       │   ├── raw_currency_rates.yml
│   │       │   └── country.yml
│   │       ├── transform/          
│   │       │   ├── dim_customers.yml
│   │       │   └── fct_invoices.yml
│   │       └── report/             
│   │           └── report_monthly_revenue.yml
│   │
│   └── keys/                      
│       └── de-project-creds.json
│
├── Dockerfile                      
├── requirements.txt                
├── airflow_settings.yaml           
├── .env                          
└── .gitignore
```

## Data Models (dbt-core)


## Data Quality testing (Soda-core)


## Data Studio (Looker) reporting 



## Reproducibility Steps

Step 1: Clone repo and configure

```
git clone git@github.com:roman-m-g/OnlineBusinessPipeline.git
cd OnlineBusinessPipeline


# create keys/ and copy service-account-key.json 
cp /path/to/your/service-account-key.json keys/de-project-creds.json
```

### Provision Infrastructure with Terraform (first time)
```
cd terraform
terraform init
terraform plan
terraform apply
```

#### Clean up
```
cd terraform
terraform destroy
```
## Prerequisites

```
1 Terraform installed
2 Docker and Docker Compose
3 Python 3.12+
4 GCP Account (billing enabled)
5 Service Account with roles: Storage Admin, BigQuery Admin
6 Service Account Key (JSON) saved as keys/de-project-creds.json
7 Google Data Studio
```

Step 2: Install and setup astro cli

https://github.com/astronomer/astro-cli

Linux  Astro cli version v1.41.0
```
curl -sSL install.astronomer.io | sudo bash -s


astro dev init


```

add to .env
```
PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
OPENLINEAGE_DISABLED=true
AIRFLOW__OPENLINEAGE__DISABLED=true
AIRFLOW__CORE__DAG_FILE_PROCESSOR_TIMEOUT=120
```

```
astro dev restart    -- astro dev start        -- astro dev stop
```

debug error - might need it - remove the old project containers manually and then restart.
```
astro dev restart --remove-orphans
```




Step 3: Get datasets and save to include/dataset/   

1 online_business.csv 

Data loaded from https://www.kaggle.com/datasets/tunguz/online-retail and converted to utf-8 and saved to include/dataset/online_business.csv 

Dataset Information:

This is a transnational data set which contains all the transactions occurring between 01/12/2010 and 09/12/2011 for a UK-based and registered non-store online retail.The company mainly sells unique all-occasion gifts. Many customers of the company are wholesalers.

Attribute Information:

InvoiceNo: Invoice number. Nominal, a 6-digit integral number uniquely assigned to each transaction. If this code starts with letter 'c', it indicates a cancellation.
StockCode: Product (item) code. Nominal, a 5-digit integral number uniquely assigned to each distinct product.
Description: Product (item) name. Nominal.
Quantity: The quantities of each product (item) per transaction. Numeric.
InvoiceDate: Invice Date and time. Numeric, the day and time when each transaction was generated.
UnitPrice: Unit price. Numeric, Product price per unit in sterling.
CustomerID: Customer number. Nominal, a 5-digit integral number uniquely assigned to each customer.
Country: Country name. Nominal, the name of the country where each customer resides.


Updated Country   EIRE to Ireland  (8196) records.


1.2 country.csv 


2 gbp_monthly_avg_2010_2026.csv

Run Dag  gbp_monthly_avg_to_gcs.py

Download from GCS bucket and save include/dataset/currency_rates_gbp_monthly_avg_2010_2026.csv 




