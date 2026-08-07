output "workload_identity_provider" {
  value       = google_iam_workload_identity_pool_provider.github_provider.name
  description = "WIF Provider ID for GitHub Actions workflow"
}

output "service_account_email" {
  value       = google_service_account.github_actions_sa.email
  description = "Service Account Email for GitHub Actions workflow"
}

output "artifact_registry_repo" {
  value       = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.docker_repo.repository_id}"
  description = "Docker Repository URL"
}
