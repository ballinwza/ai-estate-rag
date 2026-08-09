terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  # backend "gcs" {
  #   bucket = "tr-ai-estate-ragv1" # ชื่อ Bucket บน GCP สำหรับเก็บ State
  #   prefix = "terraform/state"
  # }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}
