```mermaid
graph TB
    %% Users and Clients
    Users[👨‍💻 Users]
    WebApp[🌐 Web Dashboard<br/>index_enhanced.html]
    APIClients[📱 API Clients<br/>Programmatic Access]
    
    %% API Gateway
    APIGW[🌐 API Gateway<br/>REST API Regional<br/>- POST /analyze<br/>- OPTIONS /*<br/>- GET /health]
    
    %% Lambda Function
    Lambda[🚀 AWS Lambda<br/>erasmus-analyzer<br/>Python 3.9, 1024MB]
    
    %% Lambda Internal Components
    subgraph LambdaComponents["📋 Lambda Analysis Engine"]
        CVE[🔍 CVE Analysis<br/>NVD API v2<br/>Critical/High CVEs]
        DepTrack[🏗️ Dependency Tracking<br/>Supply Chain Analysis<br/>BFS Algorithm]
        OFAC[🌍 OFAC Scanner<br/>20+ Countries<br/>Sanctions Screening]
        ExecSum[📊 Executive Summaries<br/>BLUF Reports<br/>Action Items]
        RiskEngine[⚡ Risk Engine<br/>CVSS Scoring<br/>Prioritization]
        MultiFormat[🔗 Multi-Format Support<br/>CycloneDX<br/>Multi-ecosystem]
    end
    
    %% Storage Systems
    S3[📦 S3 Bucket<br/>AES-256 Encrypted<br/>- sboms/ (input)<br/>- analysis/ (output)]
    DynamoDB[(🗄️ DynamoDB<br/>ErasmusSBOMAnalysisCache<br/>Pay-per-Request<br/>GSI: timestamp-index)]
    
    %% External APIs
    subgraph ExternalAPIs["🌐 External APIs"]
        NVDAPI[🔍 NVD API v2<br/>CVE Database<br/>CVSS Scores]
        SafetyDB[🛡️ Safety DB<br/>Python Packages<br/>Vulnerability Intel]
    end
    
    %% Monitoring
    CloudWatch[📊 CloudWatch<br/>Metrics & Logs<br/>Dashboards]
    SNS[🔔 SNS Topic<br/>Alert Notifications<br/>Email/SMS/Webhooks]
    
    %% Security & Access
    IAM[👤 IAM Roles<br/>Least Privilege<br/>Service Policies]
    
    %% S3 Event Trigger
    S3Event[🔔 S3 Event<br/>ObjectCreated:*<br/>Prefix: sboms/<br/>Suffix: .json]
    
    %% Flow Connections
    Users --> WebApp
    Users --> APIClients
    WebApp --> APIGW
    APIClients --> APIGW
    
    APIGW --> Lambda
    Lambda --> CVE
    Lambda --> DepTrack
    Lambda --> OFAC
    Lambda --> ExecSum
    Lambda --> RiskEngine
    Lambda --> MultiFormat
    
    CVE --> NVDAPI
    DepTrack --> SafetyDB
    
    Lambda --> S3
    Lambda --> DynamoDB
    S3 --> S3Event
    S3Event --> Lambda
    
    Lambda --> CloudWatch
    CloudWatch --> SNS
    
    IAM --> Lambda
    IAM --> S3
    IAM --> DynamoDB
    
    %% Styling
    classDef userClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef awsService fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef storage fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef external fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef monitoring fill:#fff8e1,stroke:#f57f17,stroke-width:2px
    classDef security fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    
    class Users,WebApp,APIClients userClass
    class APIGW,Lambda,S3Event awsService
    class S3,DynamoDB storage
    class NVDAPI,SafetyDB external
    class CloudWatch,SNS monitoring
    class IAM security
```

## 📊 Architecture Components Matrix

| Component | Type | Purpose | Key Features |
|-----------|------|---------|--------------|
| **API Gateway** | Managed Service | Entry Point | REST API, CORS, Rate Limiting |
| **Lambda Function** | Compute | Analysis Engine | Python 3.9, 1024MB, Auto-scaling |
| **S3 Bucket** | Storage | SBOM Storage | Versioning, Encryption, Event Triggers |
| **DynamoDB** | Database | Audit Logging | NoSQL, Pay-per-Request, GSI |
| **CloudWatch** | Monitoring | Observability | Metrics, Logs, Dashboards, Alarms |
| **SNS** | Messaging | Notifications | Email, SMS, Webhook Integration |
| **IAM** | Security | Access Control | Roles, Policies, Least Privilege |
| **NVD API** | External | CVE Data | Vulnerability Intelligence |
| **Safety DB** | External | Python Security | Package Vulnerability Scanning |

## 🔄 Data Flow Patterns

### Pattern 1: Web Dashboard Analysis
```
Browser → API Gateway → Lambda → CVE/OFAC Analysis → JSON Response
```

### Pattern 2: S3 Event-Driven Processing
```
SBOM Upload → S3 → Event Notification → Lambda → Analysis → Results Storage
```

### Pattern 3: Monitoring & Alerting
```
Lambda Metrics → CloudWatch → Threshold Breach → SNS → Notifications
```

## 🏗️ Infrastructure as Code Structure

```
terraform/
├── main.tf              # Core infrastructure
├── api_gateway.tf       # API Gateway configuration
├── monitoring.tf        # CloudWatch & SNS
├── variables.tf         # Input parameters
├── outputs.tf          # Export values
└── versions.tf         # Provider requirements
```

## 🔐 Security Layers

1. **Network Security**: API Gateway with CORS, Rate Limiting
2. **Identity Security**: IAM roles with least privilege access
3. **Data Security**: Encryption at rest (S3, DynamoDB) and in transit (HTTPS/TLS)
4. **Application Security**: Input validation, error handling, secure coding
5. **Operational Security**: CloudTrail logging, monitoring, alerting

## 📈 Scalability Characteristics

- **Horizontal Scaling**: Lambda auto-scales to 1000 concurrent executions
- **Storage Scaling**: S3 provides unlimited storage capacity
- **Database Scaling**: DynamoDB auto-scales read/write capacity
- **Network Scaling**: API Gateway handles high request volumes
- **Cost Optimization**: Pay-per-use model eliminates idle costs

---

*This architecture diagram provides a comprehensive view of the Erasmus SBOM Risk Analyzer's AWS infrastructure, showing all components, data flows, and integration patterns for enterprise-grade SBOM security analysis.*
