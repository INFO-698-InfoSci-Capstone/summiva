variable "aws_region" {
  type    = string
  default = "us-west-2"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "db_user" {
  type = string
  default = "summiva_user"
}

variable "db_password" {
  type      = string
  sensitive = true
  description = "Password for PostgreSQL"
}
