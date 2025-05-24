# 🏗️ Erasmus SBOM Risk Analyzer - Professional AWS Architecture Diagrams

## 📊 Overview

This directory contains professional AWS architecture diagrams for the Erasmus SBOM Risk Analyzer project. These diagrams use official AWS architecture icons to provide a clear and professional visualization of the system architecture.

## 🖼️ Available Diagrams

### 1. Main AWS Architecture (`erasmus-aws-architecture-professional.png`)

This diagram shows the complete AWS infrastructure with:

- **API Gateway**: REST API with CORS support
- **Lambda Function**: Python-based analysis engine
- **S3 Bucket**: SBOM storage with encryption
- **DynamoDB**: Results caching and audit logs
- **CloudWatch**: Metrics, logs, and dashboards
- **SNS**: Alerting and notifications
- **User Interfaces**: Web dashboard, API clients, CI/CD pipelines
- **External Integrations**: NVD API, Safety DB

### 2. Data Flow Pipeline (`erasmus-dataflow-professional.png`)

This diagram illustrates the complete data flow through the system:

- **Step 1**: SBOM Upload (Web Dashboard/API)
- **Step 2**: Lambda Analysis Engine
- **Step 3**: External API Integration (NVD, Safety DB)
- **Step 4**: Data Storage (S3, DynamoDB)
- **Step 5**: Results Generation
- **Step 6**: Monitoring and Alerting
- **Step 7**: Dashboard Visualization

## 🛠️ Source Files

The diagrams are created using draw.io, a free and open-source diagramming tool:

- `erasmus-aws-architecture.drawio` - Main architecture diagram
- `erasmus-dataflow-diagram.drawio` - Data flow pipeline diagram

These source files can be opened and edited with:
- draw.io desktop application
- Online editor at https://app.diagrams.net/

## 🔄 Exporting Diagrams

To export high-quality PNG or SVG versions of these diagrams:

1. Use the provided export script:
   ```bash
   ./export_diagrams.sh
   ```

2. Or follow the instructions in `EXPORT_INSTRUCTIONS.md`

## 🎨 Customization

These diagrams can be easily customized:

1. Open the `.drawio` files in draw.io
2. Modify services, connections, or styling
3. Export using the methods above

## 🔗 Integration with Documentation

These diagrams are referenced in:

- `README.md` - Main project README
- `README_FINAL.md` - Complete feature documentation
- `ARCHITECTURE_DETAILED.md` - Technical architecture documentation
- `ARCHITECTURE_VISUAL.md` - Visual architecture guides

## 💡 Benefits Over ASCII Diagrams

These professional AWS architecture diagrams provide several advantages over ASCII-based diagrams:

1. **Industry-Standard Visuals**: Using official AWS icons that are immediately recognizable
2. **Clearer Data Flows**: Visual arrows showing exact relationships between services
3. **Proper Scaling**: Accurate representation of system components
4. **Professional Appearance**: Enterprise-grade documentation quality
5. **Easier Maintenance**: Simple to update as architecture evolves
6. **Export Flexibility**: Available in multiple formats (PNG, SVG)

## 📋 AWS Services Represented

The diagrams include the following AWS services with their official icons:

- **Compute**: AWS Lambda
- **Storage**: S3 Bucket
- **Database**: DynamoDB
- **Networking**: API Gateway
- **Management**: CloudWatch
- **Messaging**: SNS
- **Security**: IAM Roles and Policies

## 🚀 Next Steps

As the Erasmus SBOM Risk Analyzer evolves:

1. Keep diagrams updated with architectural changes
2. Add new AWS services as they're integrated
3. Create additional diagrams for specific features
4. Use diagrams in presentations and technical documentation
