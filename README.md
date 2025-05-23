# 🧠 Erasmus Enhanced — AI-Powered SBOM Risk Analyzer

This project automates the analysis of Software Bill of Materials (SBOMs) for geopolitical and OFAC compliance risks using a fully serverless AWS architecture.

## ✅ What It Does
- 🧾 Ingests CycloneDX SBOMs from S3
- 🧠 Checks package metadata (emails, origins) for sanctioned-country indicators
- 🌍 Enriches outputs with risk levels, metadata, and audit trail
- 🗂️ Stores results in S3 and logs summary to DynamoDB

---

## 📐 Architecture

![Architecture Diagram](architecture/erasmus-architecture.png)

---

## 🧱 Stack

| Component        | Tech                  |
|------------------|------------------------|
| SBOM Format       | CycloneDX (JSON)       |
| Ingestion         | S3 Bucket (`sboms/`)   |
| Analysis Engine   | AWS Lambda (Python)    |
| Risk Mapping      | Static OFAC mappings   |
| Output            | S3 Bucket (`analysis/`)|
| Audit Logging     | DynamoDB               |

---

## 🚀 How to Deploy

```bash
cd terraform
terraform init
terraform apply