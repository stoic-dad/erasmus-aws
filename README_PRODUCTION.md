# Erasmus SBOM Risk Analyzer v2.0

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![AWS](https://img.shields.io/badge/AWS-Cloud-orange.svg)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Terraform](https://img.shields.io/badge/Terraform-Infrastructure-purple.svg)](https://terraform.io)

An AI-powered Software Bill of Materials (SBOM) security analysis platform that provides **Critical CVE Detection**, **OFAC Compliance Checking**, **Dependency Depth Analysis**, and **Executive Risk Summaries**.

## 🚀 Key Features

### 🔒 Security Analysis
- **Critical & High CVE Detection**: Real-time vulnerability scanning using NVD API v2
- **CVSS Scoring**: Automated risk scoring with actionable severity levels
- **Multi-Ecosystem Support**: Python (PyPI), Node.js (npm), Java (Maven), .NET (NuGet)

### ⚖️ Compliance & Governance  
- **OFAC Risk Detection**: Automated screening for sanctioned countries/entities
- **Executive BLUF Reports**: Bottom Line Up Front summaries for leadership
- **Regulatory Compliance**: Built-in compliance checking and reporting

### 📊 Dependency Intelligence
- **Dependency Depth Tracking**: Hierarchical analysis of direct vs transitive dependencies
- **Supply Chain Visualization**: Interactive dependency tree mapping
- **Risk Propagation Analysis**: Understanding how vulnerabilities cascade through dependencies

### 🎯 Enterprise Features
- **AWS-Native Architecture**: Serverless, scalable, and cost-effective
- **Real-time Processing**: S3-triggered automatic analysis
- **Executive Dashboards**: Leadership-ready risk assessments
- **Audit Trail**: Complete analysis history and compliance reporting

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   SBOM Upload   │───▶│   S3 Trigger     │───▶│ Lambda Analyzer │
│   (Web/API)     │    │   (Auto-detect)  │    │ (CVE + OFAC)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│Executive Summary│◀───│   DynamoDB       │◀───│ Analysis Results│
│   (BLUF/TLDR)   │    │   (Audit Trail)  │    │ (S3 Storage)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Infrastructure Components
- **AWS Lambda**: Serverless analysis engine with CVE and OFAC detection
- **Amazon S3**: SBOM storage and analysis results repository  
- **DynamoDB**: Audit logging and analysis caching
- **API Gateway**: RESTful API for web dashboard integration
- **CloudWatch**: Comprehensive monitoring and alerting

## 📋 Prerequisites

- **AWS Account** with appropriate IAM permissions
- **Terraform** v1.0+ for infrastructure deployment
- **Python** 3.9+ for local development/testing
- **NVD API Key** (optional but recommended for higher rate limits)

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/your-org/erasmus-aws-sbom-analyzer.git
cd erasmus-aws-sbom-analyzer
```

### 2. Configure Infrastructure
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your AWS settings
```

Example `terraform.tfvars`:
```hcl
project_name    = "erasmus-sbom-analyzer"
environment     = "prod"
aws_region      = "us-east-1"
nvd_api_key     = "your-nvd-api-key"  # Optional but recommended
lambda_timeout  = 300
lambda_memory_size = 1024
```

### 3. Deploy Infrastructure
```bash
terraform init
terraform plan
terraform apply
```

### 4. Test with Sample SBOM
```bash
# Upload sample SBOM to trigger analysis
aws s3 cp ../sboms/sample_sbom.json s3://your-bucket-name/sboms/
```

### 5. Access Results
- **Analysis Results**: Check S3 `analysis/` folder
- **Web Dashboard**: Open `web/index_enhanced.html` in browser
- **API Endpoint**: Use the API Gateway URL from Terraform outputs

## 📊 Usage Examples

### Upload SBOM via AWS CLI
```bash
aws s3 cp my-project-sbom.json s3://your-bucket/sboms/my-project-sbom.json
```

### Query Analysis Results
```bash
# Get latest analysis
aws s3 ls s3://your-bucket/analysis/ --recursive | tail -1

# Download specific analysis
aws s3 cp s3://your-bucket/analysis/my-project_analysis_20240524_143022.json ./
```

### Executive Summary Example
```json
{
  "executive_summary": {
    "bluf": "🚨 SBOM ANALYSIS: CRITICAL RISK - 3 critical vulnerabilities require immediate attention.",
    "recommendation": "HALT DEPLOYMENT. Address critical vulnerabilities before proceeding.",
    "risk_level": "CRITICAL",
    "key_metrics": {
      "total_components": 245,
      "vulnerable_components": 18,
      "critical_issues": 3,
      "high_issues": 12,
      "ofac_risks": 1
    }
  }
}
```

## 🔧 Configuration

### Environment Variables
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DDB_TABLE_NAME` | DynamoDB table for audit logs | Yes | Set by Terraform |
| `S3_BUCKET_NAME` | S3 bucket for SBOM storage | Yes | Set by Terraform |
| `NVD_API_KEY` | NVD API key for CVE data | No | "" |

### Lambda Configuration
- **Runtime**: Python 3.9
- **Memory**: 512MB - 1024MB (configurable)
- **Timeout**: 300 seconds (configurable)
- **Concurrent Executions**: 100 (default)

## 📈 Monitoring & Alerts

### CloudWatch Metrics
- **Analysis Success Rate**: Percentage of successful SBOM analyses
- **Processing Time**: Average time per SBOM analysis
- **Error Rate**: Failed analysis attempts
- **CVE Detection Rate**: Critical/High vulnerabilities found

### Sample CloudWatch Dashboard
```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/Lambda", "Invocations", "FunctionName", "erasmus-analyzer"],
          ["AWS/Lambda", "Errors", "FunctionName", "erasmus-analyzer"],
          ["AWS/Lambda", "Duration", "FunctionName", "erasmus-analyzer"]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "SBOM Analysis Performance"
      }
    }
  ]
}
```

## 🧪 Testing

### Unit Tests
```bash
cd lambda_function
python -m pytest test_lambda.py -v
```

### Integration Tests
```bash
# Test with sample SBOM
python test_integration.py
```

### Load Testing
```bash
# Upload multiple SBOMs concurrently
for i in {1..10}; do
  aws s3 cp sample_sbom.json s3://bucket/sboms/test_$i.json &
done
```

## 🔒 Security Considerations

### Data Protection
- **Encryption at Rest**: S3 and DynamoDB use AES-256 encryption
- **Encryption in Transit**: All API communications use TLS 1.2+
- **Access Control**: IAM roles with least-privilege permissions

### Compliance Features
- **Audit Logging**: Complete trail of all analysis activities
- **Data Retention**: Configurable retention policies
- **OFAC Screening**: Automated compliance checking for sanctioned entities

### API Security
- **Rate Limiting**: API Gateway throttling enabled
- **CORS Configuration**: Restricted to authorized domains
- **Input Validation**: Comprehensive SBOM format validation

## 🛠️ Development

### Local Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r lambda_function/requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest lambda_function/test_lambda.py
```

### Adding New CVE Sources
```python
# In lambda_function/lambda_function.py
def get_cve_data_for_package(package_name, version, ecosystem):
    # Add new CVE source integration
    additional_cves = fetch_from_new_source(package_name, version)
    return combined_cve_results
```

### Custom Risk Scoring
```python
# Modify RISK_WEIGHTS in lambda_function.py
RISK_WEIGHTS = {
    'domain_match': 0.8,
    'keyword_match': 0.6,
    'critical_cve': 1.0,
    'custom_risk_factor': 0.7  # Add custom scoring
}
```

## 📚 API Reference

### POST /analyze
Analyze SBOM content directly via API

**Request:**
```json
{
  "sbom_data": {
    "bomFormat": "CycloneDX",
    "components": [...]
  }
}
```

**Response:**
```json
{
  "summary": {
    "total_components": 150,
    "critical_cves": 2,
    "high_cves": 8,
    "ofac_risks": 0,
    "overall_risk_level": "HIGH"
  },
  "executive_summary": {...},
  "cve_analysis": {...},
  "dependency_analysis": {...}
}
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Commit changes: `git commit -m 'Add amazing feature'`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **NIST National Vulnerability Database** for CVE data
- **OFAC** for sanctions screening data
- **CycloneDX** for SBOM standardization
- **AWS** for cloud infrastructure
- **Community Contributors** for ongoing improvements

## 📞 Support

- **Documentation**: [Wiki](https://github.com/your-org/erasmus-aws-sbom-analyzer/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-org/erasmus-aws-sbom-analyzer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/erasmus-aws-sbom-analyzer/discussions)
- **Security**: Email security@yourorg.com for security issues

---

**Made with ❤️ for Supply Chain Security**

*Erasmus SBOM Risk Analyzer - Protecting your software supply chain with AI-powered analysis*
