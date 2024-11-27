
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  default     = "us-east4"
  type        = string
}

variable "image_tag" {
  description = "Tag de la imagen Docker"
  default     = "latest"
  type        = string
}

output "service_url" {
  value = google_cloud_run_service.hello_world_service.status[0].url
}