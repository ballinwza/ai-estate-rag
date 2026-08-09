output "workload_identity_provider" {
  description = "WIF Provider ID for GitHub Actions workflow"
  value       = module.application.workload_identity_provider
}

output "service_account_email" {
  value       = module.application.service_account_email
  description = "Service Account Email for GitHub Actions workflow"
}

output "artifact_registry_repo" {
  value       = module.application.artifact_registry_repo
  description = "Docker Repository URL"
}
