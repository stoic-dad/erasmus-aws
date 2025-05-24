terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.4"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Random ID for unique resource naming
resource "random_id" "bucket_suffix" {
  byte_length = 8
}

# S3 Bucket for SBOM storage
resource "aws_s3_bucket" "sbom_storage" {
  bucket = var.s3_bucket_name != "" ? var.s3_bucket_name : "${var.project_name}-${var.environment}-${random_id.bucket_suffix.hex}"
}

resource "aws_s3_bucket_versioning" "sbom_storage_versioning" {
  bucket = aws_s3_bucket.sbom_storage.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "sbom_storage_encryption" {
  bucket = aws_s3_bucket.sbom_storage.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "sbom_storage_pab" {
  bucket = aws_s3_bucket.sbom_storage.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# DynamoDB Table for audit logging
resource "aws_dynamodb_table" "sbom_analysis_cache" {
  name           = "ErasmusSBOMAnalysisCache"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "sbom_id"

  attribute {
    name = "sbom_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  global_secondary_index {
    name               = "timestamp-index"
    hash_key           = "timestamp"
    projection_type    = "ALL"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-cache"
    Environment = var.environment
    Project     = var.project_name
  }
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.project_name}-${var.environment}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Lambda to access S3 and DynamoDB
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-${var.environment}-lambda-policy"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.sbom_storage.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.sbom_storage.arn
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.sbom_analysis_cache.arn,
          "${aws_dynamodb_table.sbom_analysis_cache.arn}/*"
        ]
      }
    ]
  })
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda_logs" {
  count             = var.enable_cloudwatch_logs_retention ? 1 : 0
  name              = "/aws/lambda/${var.project_name}-${var.environment}-analyzer"
  retention_in_days = var.logs_retention_days
}

# Package Lambda function
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda_function"
  output_path = "${path.module}/lambda_function.zip"
}

# Lambda Function
resource "aws_lambda_function" "sbom_analyzer" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.project_name}-${var.environment}-analyzer"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime         = "python3.9"
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size

  environment {
    variables = {
      DDB_TABLE_NAME = aws_dynamodb_table.sbom_analysis_cache.name
      S3_BUCKET_NAME = aws_s3_bucket.sbom_storage.bucket
      NVD_API_KEY    = var.nvd_api_key
    }
  }

  depends_on = [
    aws_iam_role_policy.lambda_policy,
    aws_cloudwatch_log_group.lambda_logs,
  ]

  tags = {
    Name        = "${var.project_name}-${var.environment}-analyzer"
    Environment = var.environment
    Project     = var.project_name
  }
}

# S3 Bucket Notification for Lambda
resource "aws_s3_bucket_notification" "sbom_upload_notification" {
  bucket = aws_s3_bucket.sbom_storage.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.sbom_analyzer.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "sboms/"
    filter_suffix       = ".json"
  }

  depends_on = [aws_lambda_permission.s3_invoke_lambda]
}

# Lambda permission for S3 to invoke
resource "aws_lambda_permission" "s3_invoke_lambda" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.sbom_analyzer.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.sbom_storage.arn
}
