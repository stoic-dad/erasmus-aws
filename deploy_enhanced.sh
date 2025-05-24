#!/bin/bash

# Erasmus SBOM Risk Analyzer v2.0 - Enhanced Deployment Script
# Deploys CVE analysis, dependency tracking, and executive summary features

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="erasmus-sbom-analyzer"
ENVIRONMENT="prod"
AWS_REGION="us-east-1"

echo -e "${BLUE}🚀 Erasmus SBOM Risk Analyzer v2.0 - Enhanced Deployment${NC}"
echo -e "${BLUE}Features: CVE Analysis | OFAC Compliance | Dependency Tracking | Executive Summaries${NC}"
echo ""

# Function to print status messages
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
print_info "Checking prerequisites..."

# Check if AWS CLI is installed and configured
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    print_error "Terraform is not installed. Please install it first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install it first."
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS credentials are not configured. Please run 'aws configure' first."
    exit 1
fi

print_status "Prerequisites check completed"

# Get current AWS account info
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_USER=$(aws sts get-caller-identity --query Arn --output text | cut -d'/' -f2)

print_info "Deploying to AWS Account: $AWS_ACCOUNT_ID"
print_info "Using AWS User/Role: $AWS_USER"
print_info "Target Region: $AWS_REGION"
echo ""

# Ask for NVD API key (optional but recommended)
echo -e "${YELLOW}NVD API Key Configuration:${NC}"
echo "An NVD API key improves CVE data retrieval rate limits (optional but recommended)"
echo "Get your free API key at: https://nvd.nist.gov/developers/request-an-api-key"
read -p "Enter your NVD API key (or press Enter to skip): " NVD_API_KEY

# Validate Python dependencies
print_info "Validating Python dependencies for enhanced features..."
cd lambda_function

# Check if requirements.txt has the enhanced dependencies
if ! grep -q "nvdlib" requirements.txt; then
    print_warning "Enhanced CVE analysis dependencies not found in requirements.txt"
    print_info "Adding enhanced dependencies..."
    echo "" >> requirements.txt
    echo "# Enhanced CVE and Security Analysis Dependencies" >> requirements.txt
    echo "nvdlib>=0.7.0" >> requirements.txt
    echo "safety>=2.0.0" >> requirements.txt
    echo "packaging>=21.0" >> requirements.txt
    echo "python-dateutil>=2.8.0" >> requirements.txt
fi

# Run tests to ensure everything works
print_info "Running enhanced test suite..."
if command -v pytest &> /dev/null; then
    python3 -m pytest test_lambda.py -v
    if [ $? -eq 0 ]; then
        print_status "All tests passed - CVE analysis, dependency tracking, and executive summary features ready"
    else
        print_error "Tests failed. Please fix the issues before deployment."
        exit 1
    fi
else
    print_warning "pytest not found. Installing..."
    pip3 install pytest
    python3 -m pytest test_lambda.py -v
fi

cd ..

# Create terraform.tfvars if it doesn't exist
if [ ! -f "terraform/terraform.tfvars" ]; then
    print_info "Creating terraform.tfvars configuration..."
    cat > terraform/terraform.tfvars << EOF
# Erasmus SBOM Risk Analyzer v2.0 Configuration
project_name    = "$PROJECT_NAME"
environment     = "$ENVIRONMENT"
aws_region      = "$AWS_REGION"
nvd_api_key     = "$NVD_API_KEY"

# Enhanced Lambda Configuration for CVE Analysis
lambda_timeout     = 300
lambda_memory_size = 1024

# Monitoring Configuration
enable_cloudwatch_logs_retention = true
logs_retention_days             = 30

# Optional: Custom S3 bucket name (leave empty for auto-generation)
s3_bucket_name = ""
EOF
    print_status "Created terraform.tfvars with enhanced configuration"
else
    print_info "terraform.tfvars already exists. Please verify NVD API key is configured."
fi

# Deploy infrastructure
print_info "Deploying enhanced infrastructure with Terraform..."
cd terraform

# Initialize Terraform
terraform init
if [ $? -ne 0 ]; then
    print_error "Terraform initialization failed"
    exit 1
fi

# Plan deployment
print_info "Planning infrastructure deployment..."
terraform plan -out=tfplan
if [ $? -ne 0 ]; then
    print_error "Terraform planning failed"
    exit 1
fi

# Apply deployment
print_info "Applying infrastructure changes..."
terraform apply tfplan
if [ $? -ne 0 ]; then
    print_error "Terraform deployment failed"
    exit 1
fi

# Get outputs
S3_BUCKET=$(terraform output -raw s3_bucket_name)
API_ENDPOINT=$(terraform output -raw api_gateway_url)
LAMBDA_FUNCTION=$(terraform output -raw lambda_function_name)

cd ..

print_status "Infrastructure deployment completed successfully!"
echo ""

# Upload sample SBOM for testing
print_info "Testing deployment with sample SBOM..."
if [ -f "sboms/sample_sbom.json" ]; then
    aws s3 cp sboms/sample_sbom.json s3://$S3_BUCKET/sboms/sample_sbom.json
    print_status "Sample SBOM uploaded for testing"
    
    # Wait for analysis to complete
    print_info "Waiting for analysis to complete (30 seconds)..."
    sleep 30
    
    # Check for analysis results
    ANALYSIS_COUNT=$(aws s3 ls s3://$S3_BUCKET/analysis/ | wc -l)
    if [ $ANALYSIS_COUNT -gt 0 ]; then
        print_status "Analysis completed successfully! Enhanced features are working."
    else
        print_warning "Analysis may still be processing. Check CloudWatch logs if needed."
    fi
else
    print_warning "Sample SBOM not found. You can upload your own SBOM to test."
fi

# Display deployment summary
echo ""
echo -e "${GREEN}🎉 Erasmus SBOM Risk Analyzer v2.0 Deployment Complete!${NC}"
echo ""
echo -e "${BLUE}📊 Enhanced Features Deployed:${NC}"
echo "  ✅ Critical & High CVE Detection (NVD API v2)"
echo "  ✅ OFAC Compliance Screening"
echo "  ✅ Dependency Depth Analysis"
echo "  ✅ Executive Summary (BLUF) Generation"
echo "  ✅ Multi-ecosystem Support (PyPI, npm, Maven, NuGet)"
echo ""
echo -e "${BLUE}🔗 Access Information:${NC}"
echo "  S3 Bucket:        $S3_BUCKET"
echo "  API Endpoint:     $API_ENDPOINT"
echo "  Lambda Function:  $LAMBDA_FUNCTION"
echo "  AWS Region:       $AWS_REGION"
echo ""
echo -e "${BLUE}📚 Usage:${NC}"
echo "  1. Upload SBOM:   aws s3 cp your-sbom.json s3://$S3_BUCKET/sboms/"
echo "  2. View Results:  aws s3 ls s3://$S3_BUCKET/analysis/"
echo "  3. Download:      aws s3 cp s3://$S3_BUCKET/analysis/[file] ./"
echo "  4. Web Dashboard: Open web/index_enhanced.html in browser"
echo ""
echo -e "${YELLOW}💡 Pro Tips:${NC}"
echo "  • Use NVD API key for better CVE data rate limits"
echo "  • Check CloudWatch logs for detailed analysis information"
echo "  • Executive summaries provide BLUF reports for leadership"
echo "  • Dependency analysis shows supply chain risk propagation"
echo ""
print_status "Deployment completed successfully! Your enhanced SBOM analyzer is ready."
echo ""
