terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.18.0"
    }
  }
}

provider "google" {
  # Configuration options
  credentials = file(var.credentials)
  #   project  = "de-project-486617"
  project = var.project
  region  = "europe-west2"
}


resource "google_storage_bucket" "demo-bucket" {
  name          = var.gcs_bucket_name
  location      = var.location
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 3
    }
    action {
      type = "Delete"
    }
  }
}

# resource "google_bigquery_dataset" "online_business" {
#   dataset_id = var.bq_dataset
#   location   = var.location
# }