resource "google_project_service" "artifact_registry_api" {
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_artifact_registry_repository" "docker_repo" {
  depends_on    = [google_project_service.artifact_registry_api]
  location      = var.gcp_region
  repository_id = "${var.app_name}-repo-${var.environment}"
  description   = "Docker repository for Backend FastAPI Application"
  format        = "DOCKER"

  # 🔒 เพิ่ม Cleanup Policy เพื่อลบ Image เก่าและจำกัดจำนวนเวอร์ชัน
  cleanup_policies {
    id     = "delete-older-than-14d"
    action = "DELETE"
    condition {
      tag_state  = "ANY"
      older_than = "1209600s" # 14 วัน
    }
  }

  cleanup_policies {
    id     = "keep-recent-3-versions"
    action = "KEEP"
    most_recent_versions {
      keep_count = 3
    }
  }
}
