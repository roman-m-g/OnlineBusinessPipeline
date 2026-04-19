# Online Business Pipeline

An online business operates across multiple countries and accumulates transactional invoice data in flat CSV files. The business has no centralised analytics capability — data is siloed, unvalidated, and unavailable for reporting. The goal of this project is to build an end-to-end data pipeline that ingests raw business data, connect with currency rates, then transforms it into a dimensional model, validates data quality at each stage, and makes it available for business intelligence reporting in Data Studio.


## Architecture

## Tech Stack

## Datasets

## Project Structure

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




