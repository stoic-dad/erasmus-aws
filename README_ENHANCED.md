# 🧠 Erasmus Enhanced — AI-Powered SBOM Risk Analyzer

This project automates the analysis of Software Bill of Materials (SBOMs) for geopolitical and OFAC compliance risks using a fully serverless AWS architecture with advanced AI-powered risk assessment.

## ✅ What It Does
- 🧾 **Multi-format SBOM Support**: Ingests CycloneDX SBOMs from S3 (PyPI, npm, Maven)
- 🧠 **AI-Powered Analysis**: Advanced email domain and metadata analysis for sanctioned-country indicators  
- 🌍 **Risk Scoring**: Comprehensive risk assessment with confidence levels and categorization
- 🗂️ **Structured Storage**: Results stored in S3 with metadata and audit trail in DynamoDB
- 📊 **Real-time Monitoring**: CloudWatch dashboards and alerting
- 🌐 **Web Interface**: Modern dashboard for SBOM upload and results visualization
- 🔌 **API Gateway**: RESTful API for programmatic access

---

## 📐 Architecture

![Architecture Diagram](architecture/exports/erasmus-aws-architecture-professional.png)

### Enhanced Components:
- **S3 Bucket**: SBOM ingestion (`sboms/`) and analysis output (`analysis/`)
- **Lambda Function**: Enhanced Python analyzer with comprehensive error handling
- **DynamoDB**: Audit logging with GSI for time-based queries
- **API Gateway**: RESTful endpoints for web interface integration
- **CloudWatch**: Monitoring, logging, and alerting
- **SNS**: Alert notifications for system health

#### Data Flow Pipeline
![Data Flow Diagram](architecture/exports/erasmus-dataflow-professional.png)

---

## 🧱 Enhanced Stack

| Component        | Technology            | Enhancement                    |
|------------------|-----------------------|--------------------------------|
| SBOM Format      | CycloneDX (JSON)      | Multi-package type support    |
| Ingestion        | S3 Bucket             | Versioning & encryption       |
| Analysis Engine  | AWS Lambda (Python)   | Enhanced risk scoring         |
| Risk Mapping     | OFAC + Custom Rules   | Extended country coverage     |
| Output Storage   | S3 + DynamoDB         | Structured metadata           |
| Monitoring       | CloudWatch            | Custom dashboards & alerts   |
| Web Interface    | Modern HTML/JS        | Real-time analysis dashboard  |
| API              | API Gateway           | RESTful endpoints             |

---

## 🚀 Quick Deployment

### Prerequisites
- AWS CLI configured with appropriate permissions
- Terraform >= 1.0
- Basic understanding of SBOM formats

### One-Command Deployment
```bash
./deploy.sh [environment]
```

### Manual Deployment
```bash
cd terraform
terraform init
terraform plan -var="environment=dev"
terraform apply
```

---

## 📈 Enhanced Features

### 🔍 Advanced Risk Analysis
- **Multi-package Support**: PyPI, npm, Maven (extensible)
- **Enhanced Scoring**: Weighted risk factors with confidence levels
- **Comprehensive Coverage**: 15+ sanctioned countries and regions
- **Domain Intelligence**: TLD and keyword-based risk detection

### 📊 Risk Categories
- **HIGH** (≥80%): Direct OFAC matches, .ir/.ru domains
- **MEDIUM** (50-79%): Keyword matches, suspicious patterns  
- **LOW** (<50%): Minimal risk indicators
- **CLEAN**: No risk factors detected

### 🌐 Web Dashboard Features
- Drag-and-drop SBOM upload
- Real-time analysis visualization
- Risk factor breakdown
- Component-level details
- Processing metrics

### 📱 API Endpoints
```http
POST /analyze
Content-Type: application/json

{
  "bucket": "your-bucket",
  "key": "sboms/your-file.json"
}
```

---

## 🔧 Configuration

### Environment Variables
```bash
# Lambda Configuration
DDB_TABLE_NAME=ErasmusSBOMAnalysisCache
S3_BUCKET_NAME=your-bucket-name

# Terraform Variables  
export TF_VAR_environment=dev
export TF_VAR_aws_region=us-east-1
export TF_VAR_project_name=erasmus-sbom-analyzer
```

### Terraform Variables
See `terraform/variables.tf` for full configuration options:
- `lambda_timeout`: Function timeout (default: 300s)
- `lambda_memory_size`: Memory allocation (default: 512MB)
- `logs_retention_days`: CloudWatch log retention (default: 30 days)

---

## 📊 Monitoring & Alerting

### CloudWatch Dashboards
Access your monitoring dashboard:
```
https://console.aws.amazon.com/cloudwatch/home#dashboards:name=erasmus-{env}-dashboard
```

### Key Metrics
- Lambda invocations, errors, duration
- DynamoDB read/write capacity
- S3 object counts and sizes
- API Gateway request/response metrics

### Alerts
- Lambda error rate > 5 errors/5min
- Lambda duration > 30 seconds
- DynamoDB throttling events

---

## 🔐 Security Features

### Data Protection
- S3 bucket encryption at rest
- VPC endpoints for private communication
- IAM least-privilege access
- CloudTrail audit logging

### Compliance
- OFAC sanctions list coverage
- Audit trail for all analyses
- Immutable result storage
- Data retention policies

---

## 📝 Usage Examples

### CLI Upload
```bash
# Upload SBOM for analysis
aws s3 cp my-sbom.json s3://your-bucket/sboms/

# Check results
aws s3 ls s3://your-bucket/analysis/

# Query audit logs
aws dynamodb scan --table-name ErasmusSBOMAnalysisCache
```

### Web Interface
1. Open `web/index.html` in browser
2. Configure API Gateway URL
3. Upload SBOM file via drag-and-drop
4. View real-time analysis results

### API Integration
```python
import requests

response = requests.post(
    'https://your-api-gateway-url/analyze',
    json={'bucket': 'your-bucket', 'key': 'sboms/file.json'}
)
print(response.json())
```

---

## 🧪 Testing

### Sample Data
Use the provided sample SBOM:
```bash
aws s3 cp sboms/sample_sbom.json s3://your-bucket/sboms/
```

### Expected Output
- **Components Analyzed**: 4
- **Risk Components**: 2  
- **Risk Level**: HIGH
- **Processing Time**: ~0.5s

---

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
- name: Deploy SBOM Analyzer
  run: |
    cd terraform
    terraform init
    terraform apply -auto-approve
```

### Automated Testing
```bash
# Run Lambda function tests
python -m pytest lambda_function/tests/

# Validate Terraform
terraform validate
```

---

## 🛠️ Development

### Local Testing
```bash
# Install Lambda dependencies
pip install -r lambda_function/requirements.txt

# Run local tests
python lambda_function/lambda_function.py
```

### Adding New Package Types
1. Extend `analyze_ofac()` function
2. Add new PURL patterns
3. Update risk scoring logic
4. Add test cases

---

## 📋 Maintenance

### Regular Updates
- Review and update OFAC sanctions list
- Monitor AWS service limits
- Update Lambda runtime versions
- Review CloudWatch costs

### Troubleshooting
- Check CloudWatch logs for Lambda errors
- Verify S3 permissions and bucket policies
- Monitor DynamoDB throttling
- Review API Gateway access logs

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-enhancement`
3. Add tests for new functionality
4. Submit pull request with detailed description

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

For issues and questions:
- Check CloudWatch logs first
- Review Terraform outputs
- Consult AWS documentation
- Open GitHub issue with details

---

**Built with ❤️ for supply chain security and OFAC compliance**
