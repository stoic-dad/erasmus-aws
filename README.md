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

### Deploy Infrastructure
```bash
# Clone and navigate to project
git clone <repository-url>
cd erasmus-aws-1

# Make deployment script executable
chmod +x deploy.sh

# Deploy to development environment
./deploy.sh dev

# Or deploy to production
./deploy.sh prod
```

### Manual Deployment Steps
```bash
cd terraform
terraform init
terraform plan -var="environment=dev"
terraform apply -var="environment=dev"
```

---

## 📊 Enhanced Features

### 🔍 Advanced Risk Analysis
- **Enhanced OFAC Mappings**: 20+ sanctioned countries and regions
- **Domain Intelligence**: TLD analysis + keyword matching
- **Risk Scoring**: Weighted confidence levels (0.0-1.0)
- **Multi-source Detection**: Author emails, maintainer emails, origin metadata

### 📈 Monitoring & Alerting
- **Real-time Dashboards**: CloudWatch custom dashboards
- **Automated Alerts**: SNS notifications for high-risk components
- **Performance Metrics**: Lambda execution time, error rates
- **Audit Trail**: Complete processing history in DynamoDB

### 🌐 Web Interface
- **Modern UI**: Tailwind CSS responsive design
- **Drag & Drop**: Easy SBOM file upload
- **Real-time Results**: Live analysis status updates
- **Risk Visualization**: Interactive charts and graphs
- **Export Options**: JSON, CSV results download

---

## 🧪 Testing

### Run Lambda Tests
```bash
cd lambda_function
pip install -r requirements.txt
python -m pytest test_lambda.py -v
```

### Sample Test Cases
- Email domain extraction validation
- OFAC risk scoring accuracy
- SBOM parsing edge cases
- Error handling scenarios

---

## 📝 API Documentation

### Upload SBOM
```bash
POST /analyze
Content-Type: application/json

{
  "sbom": {
    "components": [...]
  }
}
```

### Get Analysis Results
```bash
GET /results/{sbom_id}

Response:
{
  "analysis_timestamp": "2025-05-24T10:30:00Z",
  "summary": {
    "risk_level": "HIGH",
    "ofac_risk_components": 2,
    "total_components": 15
  },
  "ofac_risks": [...]
}
```

---

## 🛠️ Advanced Configuration

### Environment Variables
```bash
# Lambda Configuration
DDB_TABLE_NAME=ErasmusSBOMAnalysisCache
S3_BUCKET_NAME=erasmus-sbom-dev-bucket
AWS_REGION=us-east-1

# Risk Analysis Tuning
RISK_THRESHOLD_HIGH=0.7
RISK_THRESHOLD_MEDIUM=0.4
ENABLE_ENHANCED_SCANNING=true
```

### Terraform Variables
```hcl
# terraform.tfvars
project_name = "erasmus-sbom-analyzer"
environment = "production"
lambda_timeout = 300
lambda_memory_size = 512
logs_retention_days = 30
```

---

## 🔐 Security Features

### Data Protection
- **S3 Encryption**: AES-256 server-side encryption
- **Access Control**: IAM roles with least privilege
- **VPC Integration**: Optional VPC deployment
- **Audit Logging**: Complete activity tracking

### Compliance
- **OFAC Screening**: Comprehensive sanctioned entity detection
- **Data Retention**: Configurable log retention policies
- **Access Monitoring**: CloudTrail integration
- **Privacy**: No sensitive data storage

---

## 📚 Sample Usage

### 1. Upload SBOM via Web Interface
1. Navigate to the web dashboard
2. Drag & drop your CycloneDX JSON file
3. Click "Analyze SBOM"
4. View real-time results and risk assessment

### 2. Programmatic Upload
```bash
# Upload SBOM to S3
aws s3 cp my-sbom.json s3://your-bucket/sboms/

# Check analysis results
aws s3 ls s3://your-bucket/analysis/

# Query audit logs
aws dynamodb scan --table-name ErasmusSBOMAnalysisCache
```

### 3. API Integration
```javascript
// Upload and analyze SBOM
const response = await fetch('/api/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ sbom: sbomData })
});

const results = await response.json();
console.log('Risk Level:', results.summary.risk_level);
```

---

## 🚨 Monitoring & Alerts

### CloudWatch Dashboards
- **System Health**: Lambda performance, error rates
- **Risk Analytics**: High-risk component trends
- **Usage Metrics**: SBOM processing volume

### Alert Conditions
- High-risk SBOM detected (risk_level = "HIGH")
- Lambda function errors > 5% error rate
- DynamoDB throttling detected
- S3 upload failures

---

## 🔧 Troubleshooting

### Common Issues

**Lambda Timeout Errors**
```bash
# Increase timeout in variables.tf
lambda_timeout = 600

# Redeploy
terraform apply
```

**S3 Permission Denied**
```bash
# Check IAM role permissions
aws iam get-role-policy --role-name erasmus-dev-lambda-role --policy-name erasmus-dev-lambda-policy
```

**DynamoDB Write Errors**
```bash
# Check CloudWatch logs
aws logs filter-log-events --log-group-name /aws/lambda/erasmus-dev-analyzer
```

### Debug Mode
```bash
# Enable detailed logging
export LAMBDA_DEBUG=true

# View real-time logs
aws logs tail /aws/lambda/erasmus-dev-analyzer --follow
```

---

## 🌟 Roadmap

### Upcoming Features
- [ ] **Multi-format Support**: SPDX, SWID integration
- [ ] **Machine Learning**: Anomaly detection for risk patterns
- [ ] **Batch Processing**: Bulk SBOM analysis capabilities
- [ ] **Integration Hub**: Jenkins, GitHub Actions plugins
- [ ] **Advanced Visualizations**: Network graphs, dependency trees
- [ ] **Custom Rules Engine**: User-defined risk criteria
- [ ] **Export Formats**: PDF reports, compliance documents

### Performance Improvements
- [ ] **Caching Layer**: Redis for frequently accessed data
- [ ] **Parallel Processing**: Multi-threaded component analysis
- [ ] **Database Optimization**: DynamoDB query optimization
- [ ] **CDN Integration**: CloudFront for web interface

---

## 🤝 Contributing

### Development Setup
```bash
# Setup development environment
git clone <repository-url>
cd erasmus-aws-1

# Install dependencies
pip install -r lambda_function/requirements.txt

# Run tests
python -m pytest lambda_function/test_lambda.py

# Deploy to dev environment
./deploy.sh dev
```

### Contribution Guidelines
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`python -m pytest`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push branch (`git push origin feature/amazing-feature`)
6. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

### Documentation
- **Architecture**: See `architecture/` directory
- **API Reference**: Available in deployed API Gateway console
- **Troubleshooting**: Check CloudWatch logs and this README

### Contact
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Security**: Email security@yourcompany.com for vulnerabilities

---

**🚀 Ready to secure your software supply chain with AI-powered SBOM analysis!**