
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0" # Especifica la versión mínima requerida
    }
  }

  required_version = ">= 1.7.0"
}

provider "google" {
  project     = var.project_id
  region      = var.region
}


resource "google_artifact_registry_repository" "fastapi-repo" {
  repository_id = "hello-world-fastapi"
  location      = var.region
  format        = "DOCKER"
}

resource "google_cloud_run_service" "hello_world_service" {
  name     = "hello-world-fastapi"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/hello-world-fastapi/app:${var.image_tag}"
        ports {
          container_port = 8080
        }
        resources {
          limits = {
            cpu    = "1"
            memory = "256Mi"
          }
        }
      }

      container_concurrency = 80
      timeout_seconds       = 300
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "0"
        "autoscaling.knative.dev/maxScale" = "1"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Hacer el servicio público
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.hello_world_service.name
  location = google_cloud_run_service.hello_world_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
