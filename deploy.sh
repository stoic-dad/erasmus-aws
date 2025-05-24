#!/bin/bash

# Erasmus SBOM Analyzer - Enhanced Deployment Script
set -e

echo "🚀 Deploying Erasmus SBOM Analyzer..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
print_status "Checking prerequisites..."

if ! command -v terraform &> /dev/null; then
    print_error "Terraform is not installed. Please install Terraform first."
    exit 1
fi

if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install AWS CLI first."
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

print_status "Prerequisites check passed ✅"

# Set environment (default to dev)
ENVIRONMENT=${1:-dev}
print_status "Deploying to environment: $ENVIRONMENT"

# Navigate to terraform directory
cd terraform

# Initialize Terraform
print_status "Initializing Terraform..."
terraform init

# Validate configuration
print_status "Validating Terraform configuration..."
terraform validate

# Plan deployment
print_status "Planning deployment..."
terraform plan -var="environment=$ENVIRONMENT" -out=tfplan

# Apply deployment
echo ""
read -p "Do you want to proceed with deployment? (y/N): " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Applying Terraform configuration..."
    terraform apply tfplan
    
    # Get outputs
    print_status "Deployment completed! 🎉"
    echo ""
    print_status "📊 Infrastructure Details:"
    terraform output
    
    # Get bucket name for testing
    BUCKET_NAME=$(terraform output -raw s3_bucket_name 2>/dev/null || echo "")
    
    if [ ! -z "$BUCKET_NAME" ]; then
        echo ""
        print_status "🧪 Testing deployment..."
        
        # Upload sample SBOM
        print_status "Uploading sample SBOM..."
        aws s3 cp ../sboms/sample_sbom.json s3://$BUCKET_NAME/sboms/
        
        # Wait for processing
        print_status "Waiting for Lambda processing (10 seconds)..."
        sleep 10
        
        # Check for analysis output
        print_status "Checking for analysis results..."
        if aws s3 ls s3://$BUCKET_NAME/analysis/ | grep -q "sample_sbom"; then
            print_status "✅ Analysis completed successfully!"
            print_status "You can view results at: s3://$BUCKET_NAME/analysis/"
        else
            print_warning "⚠️  Analysis may still be processing. Check CloudWatch logs if needed."
        fi
    fi
    
    echo ""
    print_status "🎯 Next steps:"
    echo "  1. Upload SBOM files to s3://$BUCKET_NAME/sboms/"
    echo "  2. Analysis results will appear in s3://$BUCKET_NAME/analysis/"
    echo "  3. Check DynamoDB table 'ErasmusSBOMAnalysisCache' for audit logs"
    echo "  4. Monitor CloudWatch logs for debugging"
    
else
    print_warning "Deployment cancelled."
    rm -f tfplan
fi

echo ""
print_status "Deployment script completed! 🏁"
