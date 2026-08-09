resource "google_project_service" "cloud_run_api" {
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

# 2. สร้าง Cloud Run Service (ตัวแอป)
resource "google_cloud_run_v2_service" "app" {
  name     = "${var.app_name}-${var.environment}"
  location = var.gcp_region
  ingress  = "INGRESS_TRAFFIC_ALL"

  # เลือกแบบใดแบบหนึ่ง:
  # "INGRESS_TRAFFIC_INTERNAL_ONLY" -> เรียกใช้ได้เฉพาะจากภายใน VPC/GCP เดียวกัน
  # "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER" -> เข้าถึงได้ผ่าน Cloud Load Balancer เท่านั้น สำหรับ Production
  # ingress = "INGRESS_TRAFFIC_INTERNAL_ONLY"
  template {
    containers {
      # ใช้ Image เริ่มต้นไปก่อน แล้วค่อยให้ GitHub Actions สั่ง Deploy container จริงทับทีหลัง
      image = "${var.registry_path}:${var.registry_tags}"
      ports {
        container_port = 8000
      }
    }
  }
  deletion_protection = false
  depends_on = [
    google_project_service.cloud_run_api
  ]
}

# 3. Allow unauthenticated access (อ้างอิงจากตัว Service ด้านบน)
# Closing on Production
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  project  = var.gcp_project_id
  location = google_cloud_run_v2_service.app.location
  name     = google_cloud_run_v2_service.app.name
  role     = "roles/run.invoker"
  member   = "allUsers"

  # บังคับให้สร้างตัว Cloud Run ให้เสร็จก่อนเปิด Public
  depends_on = [
    google_cloud_run_v2_service.app
  ]
}
