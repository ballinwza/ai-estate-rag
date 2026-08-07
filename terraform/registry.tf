resource "google_project_service" "artifact_registry_api" {
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_artifact_registry_repository" "docker_repo" {
  depends_on    = [google_project_service.artifact_registry_api]
  location      = var.gcp_region
  repository_id = "${var.app_name}-repo"
  description   = "Docker repository for Backend FastAPI Application"
  format        = "DOCKER"
}
