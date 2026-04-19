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

Step 1: Clone repo 

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
1 GCP Account (billing enabled)
2 Service Account with roles: Storage Admin, BigQuery Admin
3 Service Account Key (JSON) saved as keys/de-project-creds.json
4 Terraform installed
5 Docker and Docker Compose
6 Python 3.12+
7 Google Data Studio
```

Step 2: astro cli


