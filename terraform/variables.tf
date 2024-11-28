
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
}

variable "image_tag" {
  description = "Tag de la imagen Docker"
  default     = "latest"
  type        = string
}
