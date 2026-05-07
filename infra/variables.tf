variable "db_username" {
  description = "Database administrator username"
  type        = string
}

variable "db_password" {
  description = "Database administrator password"
  type        = string
  sensitive   = true # Hides it from Terraform terminal output
}

variable "notion_api_key" {
  type      = string
  sensitive = true
}

variable "notion_db_id_account" {
  type = string
}