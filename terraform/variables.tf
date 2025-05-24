variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "erasmus-sbom-analyzer"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 300
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 512
}

variable "s3_bucket_name" {
  description = "S3 bucket name for SBOM storage"
  type        = string
  default     = ""
}

variable "enable_cloudwatch_logs_retention" {
  description = "Enable CloudWatch logs retention"
  type        = bool
  default     = true
}

variable "logs_retention_days" {
  description = "CloudWatch logs retention in days"
  type        = number
  default     = 30
}

variable "nvd_api_key" {
  description = "NVD API key for CVE data access (optional - improves rate limits)"
  type        = string
  default     = ""
  sensitive   = true
}
