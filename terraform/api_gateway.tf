# API Gateway for Erasmus SBOM Analyzer
resource "aws_api_gateway_rest_api" "sbom_analyzer_api" {
  name        = "${var.project_name}-${var.environment}-api"
  description = "API for SBOM analysis and results retrieval"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-api"
    Environment = var.environment
    Project     = var.project_name
  }
}

# CORS configuration
resource "aws_api_gateway_method" "options_method" {
  rest_api_id   = aws_api_gateway_rest_api.sbom_analyzer_api.id
  resource_id   = aws_api_gateway_rest_api.sbom_analyzer_api.root_resource_id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_method_response" "options_200" {
  rest_api_id = aws_api_gateway_rest_api.sbom_analyzer_api.id
  resource_id = aws_api_gateway_rest_api.sbom_analyzer_api.root_resource_id
  http_method = aws_api_gateway_method.options_method.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration" "options_integration" {
  rest_api_id = aws_api_gateway_rest_api.sbom_analyzer_api.id
  resource_id = aws_api_gateway_rest_api.sbom_analyzer_api.root_resource_id
  http_method = aws_api_gateway_method.options_method.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_integration_response" "options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.sbom_analyzer_api.id
  resource_id = aws_api_gateway_rest_api.sbom_analyzer_api.root_resource_id
  http_method = aws_api_gateway_method.options_method.http_method
  status_code = aws_api_gateway_method_response.options_200.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# Analysis endpoint
resource "aws_api_gateway_resource" "analyze_resource" {
  rest_api_id = aws_api_gateway_rest_api.sbom_analyzer_api.id
  parent_id   = aws_api_gateway_rest_api.sbom_analyzer_api.root_resource_id
  path_part   = "analyze"
}

resource "aws_api_gateway_method" "analyze_post" {
  rest_api_id   = aws_api_gateway_rest_api.sbom_analyzer_api.id
  resource_id   = aws_api_gateway_resource.analyze_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "analyze_lambda" {
  rest_api_id = aws_api_gateway_rest_api.sbom_analyzer_api.id
  resource_id = aws_api_gateway_resource.analyze_resource.id
  http_method = aws_api_gateway_method.analyze_post.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.sbom_analyzer.invoke_arn
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.sbom_analyzer.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.sbom_analyzer_api.execution_arn}/*/*"
}

# API Gateway deployment
resource "aws_api_gateway_deployment" "api_deployment" {
  depends_on = [
    aws_api_gateway_method.analyze_post,
    aws_api_gateway_integration.analyze_lambda,
    aws_api_gateway_method.options_method,
    aws_api_gateway_integration.options_integration,
  ]

  rest_api_id = aws_api_gateway_rest_api.sbom_analyzer_api.id
  stage_name  = var.environment

  lifecycle {
    create_before_destroy = true
  }
}

# CloudWatch Log Group for API Gateway
resource "aws_cloudwatch_log_group" "api_gw" {
  name              = "API-Gateway-Execution-Logs_${aws_api_gateway_rest_api.sbom_analyzer_api.id}/${var.environment}"
  retention_in_days = var.logs_retention_days
}
