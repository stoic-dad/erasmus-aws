output "s3_bucket_name" {
  description = "Name of the S3 bucket for SBOM storage"
  value       = aws_s3_bucket.sbom_storage.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket for SBOM storage"
  value       = aws_s3_bucket.sbom_storage.arn
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.sbom_analyzer.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.sbom_analyzer.arn
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.sbom_analysis_cache.name
}

output "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table"
  value       = aws_dynamodb_table.sbom_analysis_cache.arn
}

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = var.enable_cloudwatch_logs_retention ? aws_cloudwatch_log_group.lambda_logs[0].name : null
}

output "api_gateway_url" {
  description = "URL of the API Gateway"
  value       = "https://${aws_api_gateway_rest_api.sbom_analyzer_api.id}.execute-api.${var.aws_region}.amazonaws.com/${var.environment}"
}

output "api_gateway_id" {
  description = "ID of the API Gateway"
  value       = aws_api_gateway_rest_api.sbom_analyzer_api.id
}

output "sns_topic_arn" {
  description = "ARN of the SNS topic for alerts"
  value       = aws_sns_topic.alerts.arn
}

output "cloudwatch_dashboard_url" {
  description = "URL of the CloudWatch dashboard"
  value       = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.sbom_analyzer.dashboard_name}"
}
