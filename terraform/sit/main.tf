terraform {
  required_version = ">= 1.15.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.0"
    }
  }
  backend "gcs" {
    bucket = "tr-ai-estate-ragv1"
    prefix = "terraform/state"
  }
}

module "application" {
  source            = "../modules/application"
  gcp_project_id    = var.gcp_project_id
  gcp_region        = var.gcp_region
  github_repository = var.github_repository
  app_name          = var.app_name
  environment       = var.environment
  registry_path     = var.registry_path
  registry_tags     = var.registry_tags
}
