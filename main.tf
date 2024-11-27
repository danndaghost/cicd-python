provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_artifact_registry_repository" "fastapi-repo" {
  repository_id = "hello-world-fastapi"
  location      = var.region
  format        = "DOCKER"
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  default     = "us-east4"
  type        = string
}