variable "gcp_project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "gcp_region" {
  type        = string
  description = "GCP Region for deployment"
}

variable "github_repository" {
  type        = string
  description = "GitHub Repository in 'owner/repo' format (e.g., 'my-org/my-backend-app')"
}

variable "app_name" {
  type        = string
  description = "Name of the application"
}

variable "environment" {
  type        = string
  description = "Environment of application"
}

variable "registry_path" {
  type        = string
  description = "registry_name"
}


variable "registry_tags" {
  type        = string
  description = "registry_tags"
}
