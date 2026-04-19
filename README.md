# Online Business Pipeline

An online business operates across multiple countries and accumulates transactional invoice data in flat CSV files. The business has no centralised analytics capability — data stored locally in different files, unvalidated, and unavailable for reporting. The goal of this project is to build an end-to-end data pipeline that ingests raw business data, connect with currency rates, then transforms it into a dimensional model, validates data quality at each stage, and makes it available for business intelligence reporting in Google Data Studio.


## Problem Statement

A UK-based online retail business sells across 37 countries and generates thousands of invoice transactions per month. Despite this volume, the business had no analytics capability:

- **Siloed data** — transactional records existed only as flat CSV exports with no central storage
- **No currency normalisation** — all sales were recorded in GBP with no conversion to USD or EUR, making cross-market revenue comparison impossible
- **No data quality enforcement** — nulls, duplicates, and malformed records went undetected before reporting
- **No dimensional model** — raw invoice rows could not support questions like "which country drives the most revenue?" or "what is our best-selling product?" without ad-hoc SQL on every query
- **No automated pipeline** — loading, transforming, and validating data was a manual, error-prone process

## Solution

This project delivers a fully automated end-to-end ELT pipeline that turns raw CSV exports into a validated, analytics-ready dimensional model in BigQuery, refreshable on demand.

| Problem | Solution |
|---|---|
| Flat files with no central storage | Uploaded to Google Cloud Storage as the raw data lake |
| GBP-only revenue figures | Monthly GBP → USD and EUR exchange rates loaded and joined at the fact table level |
| No data quality enforcement | Soda Core checks gate every pipeline stage — raw load, transform, and report |
| No dimensional model | dbt builds a star schema: 4 dimensions + 1 fact table + 5 pre-aggregated report tables |
| Manual, error-prone process | Apache Airflow DAG orchestrates the full pipeline end-to-end with automatic failure handling |
| No business reporting | Google Data Studio dashboards connect directly to BigQuery report tables |

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

The dbt project implements a **star schema** in BigQuery. All models are materialised as physical tables in the `online_business` dataset.

### Dimensional Model

```
                        ┌──────────────────┐
                        │  dim_datetime    │
                        │  datetime_id  PK │
                        │  year            │
                        │  month           │
                        │  day / hour      │
                        │  weekday         │
                        └────────┬─────────┘
                                 │
┌──────────────────┐    ┌────────▼──────────────────────────────┐    ┌──────────────────┐
│  dim_customers   │    │              fct_invoices             │    │   dim_product    │
│  customer_id  PK │───►│  invoice_id                           │◄───│  product_id   PK │
│  country         │    │  datetime_id  FK                      │    │  stock_code      │
│  iso             │    │  product_id   FK                      │    │  description     │
└──────────────────┘    │  customer_id  FK                      │    │  price           │
                        │  quantity                             │    └──────────────────┘
                        │  total_invoice_gbp                    │
                        │  total_invoice_usd                    │    ┌──────────────────────┐
                        │  total_invoice_eur                    │◄───│  dim_currency_rates  │
                        └───────────────────────────────────────┘    │  year_month       PK │
                                                                     │  avg_rate_gbp_usd    │
                                                                     │  avg_rate_gbp_eur    │
                                                                     └──────────────────────┘
```

### Transform Models

| Model | Description |
|---|---|
| `dim_customers` | Distinct customers with surrogate key from `CustomerID + Country`. Joins to `country` table for ISO code. Excludes null customer IDs. |
| `dim_product` | Distinct products with surrogate key from `StockCode + Description + UnitPrice`. Excludes null codes and zero/negative prices. |
| `dim_datetime` | Parsed invoice timestamps with extracted year, month, day, hour, minute, weekday. Handles two raw date formats. |
| `dim_currency_rates` | Distinct monthly GBP→USD and GBP→EUR exchange rates from `raw_currency_rates`. |
| `fct_invoices` | Central fact table joining all dimensions. Calculates `total = Quantity × UnitPrice` and converts to GBP, USD, EUR by matching `year_month` to currency rates. Excludes negative quantities (cancellations). |

### Report Models

| Model | Description |
|---|---|
| `report_country_revenue` | Revenue, invoice count, and quantity sold aggregated by country + ISO code. Ordered by GBP revenue desc. |
| `report_customer_segments` | Per-customer order count, quantity, revenue (3 currencies), and average order value in GBP. |
| `report_monthly_revenue` | Month-by-month invoice count, quantity, and revenue in GBP / USD / EUR. |
| `report_product_performance` | Per-product revenue and invoice count in all three currencies. |
| `report_product_invoices` | Per-product total quantity sold. |

### dbt Packages

| Package | Version | Usage |
|---|---|---|
| `dbt-labs/dbt_utils` | 1.3.3 | `generate_surrogate_key()` macro used in dim_customers, dim_product, fct_invoices |

## Data Quality testing (Soda-core)

Data quality is enforced at three points in the pipeline using [Soda Core](https://docs.soda.io/soda-core/overview-main.html) (`soda-core-bigquery`). Each check runs inside a dedicated `soda_venv` via `@task.external_python` to keep Soda's dependencies isolated from Airflow. If any check fails (exit code 2), the task raises an exception and the DAG stops — downstream dbt transforms never run on bad data.

### How it works

```
Airflow task (@task.external_python)
  └── soda_venv/bin/python
        └── include/soda/check_function.py :: check(scan_name, checks_subpath)
              ├── loads include/soda/configuration.yml   (BigQuery connection)
              └── loads include/soda/checks/<subpath>/   (check definitions)
```

### Check stages

| Airflow task | checks_subpath | Runs after | Purpose |
|---|---|---|---|
| `check_load` | `sources` | Raw BQ load | Validate raw table schema and nulls before any transformation |
| `check_transform` | `transform` | dbt transform | Validate dimensional model schema, uniqueness, and integrity |
| `check_report` | `report` | dbt report | Validate report tables before BI consumption |

### Checks per table

**Sources** — run after `gcs_*_to_bq_raw` tasks

| Table | Check type | Detail |
|---|---|---|
| `raw_invoices` | Schema | Required columns: InvoiceNo, StockCode, Quantity, InvoiceDate, UnitPrice, CustomerID, Country |
| `raw_invoices` | Schema | Column types: Quantity → integer, UnitPrice/CustomerID → float64, others → string |
| `raw_currency_rates` | Schema | Required columns: year_month, avg_rate_gpb_usd, avg_rate_gpb_eur |
| `raw_currency_rates` | Schema | Column types: year_month → string, rates → float64 |
| `country` | Nulls | No nulls in id, iso, nicename · row_count > 0 |

**Transform** — run after dbt transform models

| Table | Check type | Detail |
|---|---|---|
| `dim_customers` | Schema | Required columns: customer_id, country · types: string |
| `dim_customers` | Uniqueness | No duplicate customer_id values |
| `dim_customers` | Nulls | No nulls in customer_id |
| `fct_invoices` | Schema | Required columns: invoice_id, product_id, customer_id, datetime_id, quantity, total_invoice_gbp |
| `fct_invoices` | Schema | Column types: IDs → string, quantity → int, total_invoice_gbp → float64 |
| `fct_invoices` | Nulls | No nulls in invoice_id |
| `fct_invoices` | Custom SQL | No rows where total_invoice_gbp < 0 (catches unfiltered cancellations) |

**Report** — run after dbt report models

| Table | Check type | Detail |
|---|---|---|
| `report_monthly_revenue` | Schema | Required columns: year, month, num_invoices, total_quantity, total_revenue_gbp, total_revenue_usd, total_revenue_eur |
| `report_monthly_revenue` | Row count | row_count > 0 |
| `report_monthly_revenue` | Nulls | No nulls in month |

### Adding new checks

Drop a `.yml` file into the relevant `include/soda/checks/<subpath>/` directory using [SodaCL syntax](https://docs.soda.io/soda-cl/soda-cl-overview.html). Soda picks up all `.yml` files in the directory automatically.

```yaml
checks for <table_name>:
  - schema:
      fail:
        when required column missing: [col1, col2]
        when wrong column type:
          col1: string
          col2: float64
  - missing_count(col1) = 0:
      name: Descriptive check name
  - failed rows:
      name: Custom business rule
      fail query: |
        SELECT id FROM <table_name> WHERE <condition>
```

Soda picks up all `.yml` files in the directory automatically — no code changes needed.



## Google Data Studio (Looker) reporting 


![DataStudioRevenueReport](pics/DataStudioRevenueReport.png.png)

18,532 total invoices processed
5,167,812 total units sold across all orders
$14,236,876 total revenue generated in USD — the key business metric


Revenue Trend Over Time (2010–2011) — line chart

This tracks monthly revenue in three currencies simultaneously — EUR (blue), GBP (orange), and USD (purple). 

Number of Invoices (2010–2011) — bar chart

This compares invoice count month by month between 2011 (blue) and 2010 (orange). Key takeaways:


2011 invoices grow steadily across the year, starting around 1K in January and reaching nearly 2K by October

The growth trend in invoice count mirrors the revenue trend above, confirming the business is growing through more transactions, not just higher order values.


![DataStudioGeorgraphicAnalysis](pics/DataStudioGeorgraphicAnalysis.png)
[Data Studio dashboard](https://datastudio.google.com/s/uBT4DbZvENc)


37 countries generated revenue — good international 

Revenue by Country 

The UK dominates overwhelmingly with ~$10M+ in revenue, while every other country is barely visible in comparison.


Total Revenue (USD) vs No. Invoices by Country

Circle colour intensity represents Total Revenue USD (up to $11,672,540)
The large dark bubble sitting over Western Europe is UK. The smaller, lighter bubbles scattered across Europe, North America, Asia and Australia represent the long-tail markets from the bar chart. The map legend confirms the largest revenue bubble reaches $11,672,540.






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



### Airflow DAG Flow 

astro dev start  executed

Access Airflow UI at http://localhost:8080


#### Currency rates GBP to USD & EUR 2010-2026 Dag

http://localhost:8080/dags/gbp_monthly_avg_to_gcs

![CurrencyRates](pics/CurrencyRates2010_2026.png)

###  Online Business Pipeline Dag

http://localhost:8080/dags/online_business/

![OnlineBusinessPipelineDag](pics/OnlineBusinessPipelineDag.png)






## Google Data Studio 

- Open [DataStudio](https://datastudio.google.com)

- Create a new report → Data Source → BigQuery

- Connect to your project → online_busines dataset

- Add report_country_revenue, report_customer_segments, report_monthly_revenue, and report_product_performance tables

- Build the two-page [dashboard](https://datastudio.google.com/s/uBT4DbZvENc)




#### Clean up

```
astro dev stop 
```


```
cd terraform
terraform destroy
```



