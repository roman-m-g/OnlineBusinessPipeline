variable "credentials" {
  description = "Path to GCP service account key file"
  default     = "./keys/de-project-creds.json"
}


variable "project" {
  description = "GCP Project ID"
  default     = "de-project-486617"
}


variable "location" {
  description = "Project Location"
  default     = "EU"
}


variable "gcs_bucket_name" {
  description = "OBP Storage Bucket Name"
  default     = "obp-486617"
}

variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  default     = "STANDARD"
}

