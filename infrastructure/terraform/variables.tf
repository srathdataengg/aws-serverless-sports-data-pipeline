variable "aws_region" {
  type        = string
  default     = "ap-south-1"
}

variable "bucket_name" {
  type = string
}

variable "lambda_zip_path" {
  type        = string
  description = "Path to lambda_code.zip"
}

variable "api_token" {
  description = "API Auth Token"
  type        = string
  sensitive   = true
}

