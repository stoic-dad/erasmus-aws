# 🏗️ Erasmus SBOM Risk Analyzer - Detailed AWS Architecture

## 📐 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           🧠 Erasmus SBOM Risk Analyzer v2.0                              │
│                                 AWS Cloud Architecture                                    │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   👨‍💻 Users      │    │  🌐 Web App     │    │  📱 API Clients │
│                 │    │  (Dashboard)    │    │  (Programmatic) │
│                 │    │                 │    │                 │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                             🌐 API Gateway (Regional)                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                         │
│  │ POST /analyze   │  │ OPTIONS (CORS)  │  │ GET /health     │                         │
│  │ (SBOM Analysis) │  │ (Preflight)     │  │ (Status Check)  │                         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                         │
└─────────────────────────────────┬───────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           🚀 AWS Lambda Function                                          │
│                      erasmus-[env]-analyzer (Python 3.9)                                │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                         📋 Core Analysis Engine                                     │ │
│  │                                                                                     │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                    │ │
│  │  │ 🔍 CVE Analysis │  │ 🏗️ Dependency   │  │ 🌍 OFAC Scanner │                    │ │
│  │  │ (NVD API v2)    │  │ Depth Tracking  │  │ (20+ Countries) │                    │ │
│  │  │ • Critical CVEs │  │ • Supply Chain  │  │ • Sanctioned    │                    │ │
│  │  │ • CVSS Scoring  │  │ • BFS Algorithm │  │   Entities      │                    │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘                    │ │
│  │                                                                                     │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                    │ │
│  │  │ 📊 Executive    │  │ 🔗 Multi-Format │  │ ⚡ Risk Engine  │                    │ │
│  │  │ Summaries       │  │ SBOM Support    │  │ (BLUF Reports)  │                    │ │
│  │  │ • BLUF/TLDR     │  │ • CycloneDX     │  │ • Action Items  │                    │ │
│  │  │ • Recommendations│  │ • Multi-ecosystem│  │ • Prioritization│                    │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘                    │ │
│  └─────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                           │
│  Configuration:                                                                          │
│  • Memory: 1024MB                                                                       │
│  • Timeout: 300s                                                                        │
│  • Runtime: Python 3.9                                                                 │
│  • Environment Variables: DDB_TABLE_NAME, S3_BUCKET_NAME, NVD_API_KEY                  │
└─────────────┬─────────────────────────────┬─────────────────────────────┬───────────────┘
              │                             │                             │
              ▼                             ▼                             ▼
┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────┐
│   📦 S3 Bucket          │    │  🗄️ DynamoDB Table     │    │  🌐 External APIs      │
│   (Object Storage)      │    │  (NoSQL Database)      │    │  (Third-party)         │
│                         │    │                        │    │                        │
│ ┌─────────────────────┐ │    │ ┌─────────────────────┐ │    │ ┌─────────────────────┐ │
│ │ 📁 sboms/           │ │    │ │ Primary Key:        │ │    │ │ 🔍 NVD API v2      │ │
│ │ • Input SBOMs       │ │    │ │ sbom_id (String)    │ │    │ │ • CVE Database     │ │
│ │ • .json files       │ │    │ │                     │ │    │ │ • CVSS Scores      │ │
│ │ • Auto-trigger      │ │    │ │ GSI: timestamp-index│ │    │ │ • Multi-ecosystem  │ │
│ └─────────────────────┘ │    │ │ • Time-based queries│ │    │ └─────────────────────┘ │
│                         │    │ │                     │ │    │                        │
│ ┌─────────────────────┐ │    │ │ Audit Data:         │ │    │ ┌─────────────────────┐ │
│ │ 📁 analysis/        │ │    │ │ • Analysis results  │ │    │ │ 🛡️ Safety DB       │ │
│ │ • Output reports    │ │    │ │ • Processing times  │ │    │ │ • Python packages  │ │
│ │ • JSON format       │ │    │ │ • Request metadata  │ │    │ │ • Vulnerability     │ │
│ │ • Timestamped       │ │    │ │ • Source tracking   │ │    │ │   Intelligence     │ │
│ └─────────────────────┘ │    │ └─────────────────────┘ │    │ └─────────────────────┘ │
│                         │    │                        │    │                        │
│ Features:               │    │ Billing Mode:          │    │ Rate Limiting:         │
│ • Versioning Enabled    │    │ • Pay-per-Request      │    │ • 5 requests/30 sec    │
│ • AES-256 Encryption    │    │ • Auto-scaling         │    │ • API Key support      │
│ • Public Access Blocked │    │ • Global consistency   │    │ • Retry mechanisms     │
│ • Object Lifecycle      │    │ • Point-in-time backup │    │ • Error handling       │
└─────────────────────────┘    └─────────────────────────┘    └─────────────────────────┘
              │                             │
              ▼                             │
┌─────────────────────────┐                 │
│  🔔 S3 Event            │                 │
│  Notifications          │                 │
│                         │                 │
│ ┌─────────────────────┐ │                 │
│ │ Trigger Conditions: │ │                 │
│ │ • s3:ObjectCreated:*│ │                 │
│ │ • Prefix: sboms/    │ │                 │
│ │ • Suffix: .json     │ │                 │
│ │ • Auto-invokes Λ    │ │                 │
│ └─────────────────────┘ │                 │
└─────────────────────────┘                 │
                                            │
┌─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                          📊 CloudWatch Monitoring & Alerting                             │
│                                                                                           │
│ ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐                │
│ │ 📈 Metrics          │  │ 🚨 Alarms           │  │ 📋 Dashboards       │                │
│ │                     │  │                     │  │                     │                │
│ │ • Lambda Duration   │  │ • Error Rate > 5%   │  │ • System Health     │                │
│ │ • Error Rates       │  │ • Duration > 30s    │  │ • Risk Analytics    │                │
│ │ • Memory Usage      │  │ • DynamoDB Throttles│  │ • Usage Metrics     │                │
│ │ • Invocation Count  │  │ • Critical CVEs     │  │ • Performance Trends│                │
│ │ • DynamoDB Metrics  │  │ • OFAC Violations   │  │ • Error Analysis    │                │
│ │ • S3 Operations     │  │ • S3 Upload Failures│  │ • Cost Tracking     │                │
│ └─────────────────────┘  └─────────────────────┘  └─────────────────────┘                │
│                                   │                                                       │
│                                   ▼                                                       │
│ ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│ │                           🔔 SNS Notifications                                     │ │
│ │                                                                                     │ │
│ │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                    │ │
│ │  │ 📧 Email Alerts │  │ 📱 SMS Alerts   │  │ 🔗 Webhook      │                    │ │
│ │  │ • Admin Team    │  │ • On-call Staff │  │ Integration     │                    │ │
│ │  │ • Daily Reports │  │ • Critical Only │  │ • Slack/Teams   │                    │ │
│ │  └─────────────────┘  └─────────────────┘  └─────────────────┘                    │ │
│ └─────────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              🔐 Security & Access Control                                 │
│                                                                                           │
│ ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐                │
│ │ 👤 IAM Roles        │  │ 🔒 Encryption       │  │ 🛡️ Network Security │                │
│ │                     │  │                     │  │                     │                │
│ │ • Lambda Execution  │  │ • S3: AES-256       │  │ • CORS Configuration│                │
│ │ • Least Privilege   │  │ • DynamoDB: Default │  │ • Regional Endpoints│                │
│ │ • Service Policies  │  │ • In-transit: TLS   │  │ • Private VPC Option│                │
│ │ • Cross-service     │  │ • API Gateway: HTTPS│  │ • Security Groups   │                │
│ └─────────────────────┘  └─────────────────────┘  └─────────────────────┘                │
│                                                                                           │
│ ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐                │
│ │ 📝 Audit Logging    │  │ 🔍 Compliance       │  │ 🚫 Access Control   │                │
│ │                     │  │                     │  │                     │                │
│ │ • CloudTrail        │  │ • OFAC Screening    │  │ • API Rate Limiting │                │
│ │ • All API Calls     │  │ • Data Retention    │  │ • S3 Public Blocked │                │
│ │ • Change Tracking   │  │ • Privacy Controls  │  │ • Resource Tagging  │                │
│ │ • Forensic Analysis │  │ • Audit Requirements│  │ • Environment Isolation│               │
│ └─────────────────────┘  └─────────────────────┘  └─────────────────────┘                │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow Architecture

### 1. Web Dashboard Flow
```
User Browser → API Gateway → Lambda → External APIs
      ↓
Web Dashboard ← API Gateway ← Lambda ← Analysis Results
```

### 2. S3 Event-Driven Flow
```
SBOM Upload → S3 Bucket → Event Notification → Lambda → Analysis
                                                   ↓
DynamoDB ← Results Storage ← S3 Analysis Output ←─┘
```

### 3. Monitoring Flow
```
Lambda Metrics → CloudWatch → Alarms → SNS → Notifications
      ↓
Custom Dashboards ← CloudWatch Logs ← Application Logs
```

## 📊 Component Details

### 🚀 Lambda Function Specifications
- **Runtime**: Python 3.9
- **Memory**: 1024MB (enhanced for CVE analysis)
- **Timeout**: 300 seconds
- **Architecture**: x86_64
- **Deployment Package**: ~15MB (with dependencies)
- **Concurrent Executions**: 1000 (default AWS limit)

### 📦 S3 Bucket Configuration
- **Storage Class**: Standard (with Intelligent Tiering option)
- **Versioning**: Enabled for audit trail
- **Encryption**: AES-256 server-side encryption
- **Public Access**: Completely blocked
- **Lifecycle**: 90-day transition to IA, 365-day to Glacier

### 🗄️ DynamoDB Table Schema
```json
{
  "TableName": "ErasmusSBOMAnalysisCache",
  "PartitionKey": "sbom_id",
  "GlobalSecondaryIndexes": [
    {
      "IndexName": "timestamp-index",
      "PartitionKey": "timestamp"
    }
  ],
  "BillingMode": "PAY_PER_REQUEST"
}
```

### 🌐 API Gateway Configuration
- **Type**: REST API (Regional)
- **Endpoints**: 
  - `POST /analyze` - SBOM analysis
  - `OPTIONS /*` - CORS preflight
  - `GET /health` - Health check
- **Authentication**: None (public API)
- **Rate Limiting**: 10,000 requests per second
- **CORS**: Enabled for web dashboard

## 🔄 Integration Patterns

### External API Integration
- **NVD API v2**: CVE vulnerability data
- **Safety DB**: Python package vulnerability scanning
- **Rate Limiting**: Exponential backoff with jitter
- **Error Handling**: Circuit breaker pattern

### Event-Driven Architecture
- **S3 Events**: Automatic SBOM processing
- **CloudWatch Events**: Scheduled health checks
- **SNS Fan-out**: Multi-channel alerting

### Caching Strategy
- **DynamoDB**: Analysis results caching
- **Lambda**: In-memory caching for OFAC data
- **API Gateway**: Response caching (optional)

## 📈 Scalability & Performance

### Auto-Scaling Components
- **Lambda**: Automatic concurrency scaling
- **DynamoDB**: On-demand billing with auto-scaling
- **API Gateway**: Managed scaling
- **S3**: Unlimited storage capacity

### Performance Optimizations
- **Lambda Layers**: Shared dependencies
- **Connection Pooling**: Database connections
- **Async Processing**: Non-blocking I/O operations
- **Batch Operations**: Bulk DynamoDB writes

## 🔐 Security Architecture

### Defense in Depth
1. **Perimeter Security**: API Gateway with rate limiting
2. **Identity & Access**: IAM roles with least privilege
3. **Data Protection**: Encryption at rest and in transit
4. **Application Security**: Input validation and sanitization
5. **Monitoring**: Real-time threat detection

### Compliance Framework
- **Data Residency**: Single AWS region deployment
- **Audit Trail**: Complete request/response logging
- **Privacy**: No persistent storage of sensitive data
- **Retention**: Configurable log retention policies

## 🚨 Disaster Recovery

### Backup Strategy
- **S3**: Cross-region replication (optional)
- **DynamoDB**: Point-in-time recovery enabled
- **Lambda**: Code versioning and aliases
- **Infrastructure**: Terraform state backup

### Recovery Procedures
- **RTO**: Recovery Time Objective < 1 hour
- **RPO**: Recovery Point Objective < 15 minutes
- **Automation**: Infrastructure as Code deployment
- **Testing**: Quarterly DR drills

## 💰 Cost Optimization

### Pay-per-Use Components
- **Lambda**: Per-request and duration billing
- **DynamoDB**: Pay-per-request pricing
- **S3**: Usage-based storage costs
- **API Gateway**: Per-request pricing

### Cost Control Measures
- **CloudWatch**: Cost and usage monitoring
- **Resource Tagging**: Cost allocation tracking
- **Lifecycle Policies**: Automated data archival
- **Right-sizing**: Optimal resource configuration

---

## 🎯 Architecture Benefits

### ✅ **Scalability**
- Serverless architecture scales automatically
- No infrastructure management required
- Handles traffic spikes gracefully

### ✅ **Reliability** 
- Multi-AZ deployment for high availability
- Automatic failover and recovery
- Comprehensive monitoring and alerting

### ✅ **Security**
- End-to-end encryption
- Network isolation and access controls
- Compliance-ready architecture

### ✅ **Cost-Effectiveness**
- Pay-per-use pricing model
- No idle resource costs
- Optimized for variable workloads

### ✅ **Maintainability**
- Infrastructure as Code (Terraform)
- Automated deployments
- Comprehensive documentation

---

*This architecture supports enterprise-grade SBOM analysis with advanced CVE detection, dependency tracking, and executive reporting capabilities while maintaining security, scalability, and cost-effectiveness.*
