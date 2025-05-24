import pytest
import json
import os
import sys
import boto3
from unittest.mock import patch, MagicMock
from moto import mock_aws

# Set up AWS environment variables for testing
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'

# Add the lambda function directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import after setting environment variables
from lambda_function import (
    extract_domain_from_email,
    check_domain_for_ofac_risk,
    calculate_component_risk_score,
    analyze_ofac,
    lambda_handler,
    get_cve_data_for_package,
    calculate_dependency_depth,
    generate_executive_summary
)

class TestEmailDomainExtraction:
    """Test email domain extraction functionality."""
    
    def test_valid_email(self):
        assert extract_domain_from_email("user@example.com") == "example.com"
        assert extract_domain_from_email("test@iran.ir") == "iran.ir"
        assert extract_domain_from_email("admin@subdomain.domain.com") == "subdomain.domain.com"
    
    def test_invalid_email(self):
        assert extract_domain_from_email("invalid") is None
        assert extract_domain_from_email("") is None
        assert extract_domain_from_email(None) is None
        assert extract_domain_from_email("user@") is None
        assert extract_domain_from_email("@domain.com") is None

class TestOFACRiskChecking:
    """Test OFAC risk checking functionality."""
    
    def test_high_risk_domains(self):
        country, confidence = check_domain_for_ofac_risk("example.ir")
        assert country == "Iran"
        assert confidence == 0.8
        
        country, confidence = check_domain_for_ofac_risk("test.ru")
        assert country == "Russia"
        assert confidence == 0.8
    
    def test_keyword_matches(self):
        country, confidence = check_domain_for_ofac_risk("tehran-company.com")
        assert country == "Iran"
        assert confidence == 0.6
    
    def test_safe_domains(self):
        country, confidence = check_domain_for_ofac_risk("example.com")
        assert country is None
        assert confidence == 0.0
        
        country, confidence = check_domain_for_ofac_risk("github.io")
        assert country is None
        assert confidence == 0.0

        country, confidence = check_domain_for_ofac_risk("google.com")
        assert country is None
        assert confidence == 0.0

class TestCVEAnalysis:
    """Test CVE analysis functionality."""
    
    @patch('lambda_function.requests.get')
    def test_get_cve_data_success(self, mock_get):
        # Mock successful NVD API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "vulnerabilities": [
                {
                    "cve": {
                        "id": "CVE-2021-23337",
                        "descriptions": [
                            {"lang": "en", "value": "Test vulnerability description"}
                        ],
                        "published": "2021-04-12T14:15:13.000",
                        "lastModified": "2021-04-12T14:15:13.000",
                        "metrics": {
                            "cvssMetricV31": [
                                {
                                    "cvssData": {
                                        "baseScore": 9.1,
                                        "baseSeverity": "CRITICAL"
                                    }
                                }
                            ]
                        }
                    }
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = get_cve_data_for_package("lodash", "4.17.20", "npm")
        
        assert len(result) == 1
        assert result[0]["cve_id"] == "CVE-2021-23337"
        assert result[0]["cvss_score"] == 9.1
        assert result[0]["severity"] == "CRITICAL"
    
    @patch('lambda_function.requests.get')
    def test_get_cve_data_api_failure(self, mock_get):
        # Mock API failure
        mock_get.side_effect = Exception("API unavailable")
        
        result = get_cve_data_for_package("lodash", "4.17.20", "npm")
        assert result == []
    
    def test_get_cve_data_empty_params(self):
        result = get_cve_data_for_package("", "", "npm")
        assert result == []

class TestDependencyAnalysis:
    """Test dependency depth analysis functionality."""
    
    def test_calculate_dependency_depth_simple(self):
        components = [
            {"name": "component1", "purl": "pkg:npm/component1@1.0.0"},
            {"name": "component2", "purl": "pkg:npm/component2@2.0.0"},
            {"name": "component3", "purl": "pkg:npm/component3@3.0.0"}
        ]
        
        result = calculate_dependency_depth(components)
        
        assert result["total_dependencies"] == 3
        assert result["max_depth"] >= 0
        assert "depth_distribution" in result
        assert "dependency_tree" in result
    
    def test_calculate_dependency_depth_empty(self):
        result = calculate_dependency_depth([])
        
        assert result["total_dependencies"] == 0
        assert result["max_depth"] == 0
        assert result["direct_dependencies"] == 0
        assert result["transitive_dependencies"] == 0

class TestExecutiveSummary:
    """Test executive summary generation."""
    
    def test_generate_executive_summary_critical_risk(self):
        analysis_results = {
            "analysis_timestamp": "2024-05-24T10:00:00Z",
            "summary": {"total_components": 100},
            "cve_analysis": {
                "critical_cves": [
                    {"cve_id": "CVE-2021-1234", "cvss_score": 9.5, "component": "test-lib"}
                ],
                "high_cves": [],
                "components_with_cves": 1
            },
            "dependency_analysis": {"max_depth": 5, "direct_dependencies": 10, "transitive_dependencies": 90},
            "ofac_risks": []
        }
        
        result = generate_executive_summary(analysis_results)
        
        assert result["risk_level"] == "CRITICAL"
        assert "CRITICAL RISK" in result["bluf"]
        assert "HALT DEPLOYMENT" in result["recommendation"]
        assert result["action_required"] == True
        assert result["key_metrics"]["total_components"] == 100
    
    def test_generate_executive_summary_low_risk(self):
        analysis_results = {
            "analysis_timestamp": "2024-05-24T10:00:00Z",
            "summary": {"total_components": 50},
            "cve_analysis": {"critical_cves": [], "high_cves": [], "components_with_cves": 0},
            "dependency_analysis": {"max_depth": 3, "direct_dependencies": 15, "transitive_dependencies": 35},
            "ofac_risks": []
        }
        
        result = generate_executive_summary(analysis_results)
        
        assert result["risk_level"] == "LOW"
        assert "LOW RISK" in result["bluf"]
        assert "Proceed with deployment" in result["recommendation"]
        assert result["action_required"] == False

class TestEnhancedAnalysis:
    """Test enhanced SBOM analysis with CVE and dependency features."""
    
    @patch('lambda_function.get_cve_data_for_package')
    def test_analyze_ofac_with_cve_integration(self, mock_cve_func):
        # Mock CVE data
        mock_cve_func.return_value = [
            {
                "cve_id": "CVE-2021-1234",
                "cvss_score": 9.1,
                "severity": "CRITICAL",
                "description": "Test critical vulnerability",
                "published_date": "2021-04-12T14:15:13.000",
                "last_modified": "2021-04-12T14:15:13.000"
            }
        ]
        
        sbom_data = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.4",
            "components": [
                {
                    "name": "lodash",
                    "version": "4.17.20",
                    "purl": "pkg:npm/lodash@4.17.20",
                    "properties": [
                        {"name": "author_email", "value": "test@example.com"}
                    ]
                }
            ]
        }
        
        result = analyze_ofac(sbom_data)
        
        # Verify enhanced analysis structure
        assert "cve_analysis" in result
        assert "dependency_analysis" in result
        assert "executive_summary" in result
        assert result["cve_analysis"]["total_cves_found"] >= 0
        assert result["cve_analysis"]["components_with_cves"] >= 0
        assert "max_depth" in result["dependency_analysis"]
        assert result["executive_summary"]["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

@mock_aws
class TestLambdaHandler:
    """Test Lambda handler functionality."""
    
    def setup_method(self, method):
        """Set up test environment."""
        # Create mock S3 bucket
        self.s3_client = boto3.client('s3', region_name='us-east-1')
        self.bucket_name = 'test-bucket'
        self.s3_client.create_bucket(Bucket=self.bucket_name)
        
        # Create mock DynamoDB table
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.table = self.dynamodb.create_table(
            TableName='ErasmusSBOMAnalysisCache',
            KeySchema=[
                {'AttributeName': 'sbom_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'sbom_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Sample SBOM data
        self.sample_sbom = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.4",
            "components": [
                {
                    "name": "test-package",
                    "version": "1.0.0",
                    "purl": "pkg:pypi/test-package@1.0.0",
                    "properties": [
                        {
                            "name": "author_email",
                            "value": "test@iran.ir"
                        }
                    ]
                }
            ]
        }
    
    def test_s3_event_trigger(self):
        """Test Lambda handler with S3 event."""
        # Upload test SBOM to S3
        key = 'sboms/test-sbom.json'
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=json.dumps(self.sample_sbom)
        )
        
        # Create S3 event
        event = {
            'Records': [{
                's3': {
                    'bucket': {'name': self.bucket_name},
                    'object': {'key': key}
                }
            }]
        }
        
        context = MagicMock()
        context.aws_request_id = 'test-request-id'
        
        with patch.dict(os.environ, {'DDB_TABLE_NAME': 'ErasmusSBOMAnalysisCache'}):
            response = lambda_handler(event, context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'summary' in body
        assert body['summary']['total_components'] == 1
    
    def test_invalid_file_format(self):
        """Test handler with non-JSON file."""
        event = {
            'Records': [{
                's3': {
                    'bucket': {'name': self.bucket_name},
                    'object': {'key': 'sboms/test.txt'}
                }
            }]
        }
        
        context = MagicMock()
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 200
        assert 'Not a SBOM file' in response['body']
    
    def test_missing_s3_object(self):
        """Test handler with missing S3 object."""
        event = {
            'Records': [{
                's3': {
                    'bucket': {'name': self.bucket_name},
                    'object': {'key': 'sboms/missing-file.json'}
                }
            }]
        }
        
        context = MagicMock()
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 500
    
    def test_direct_invocation(self):
        """Test Lambda handler with direct invocation."""
        # Upload test SBOM to S3
        key = 'sboms/direct-test.json'
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=json.dumps(self.sample_sbom)
        )
        
        event = {
            'bucket': self.bucket_name,
            'key': key
        }
        
        context = MagicMock()
        context.aws_request_id = 'test-request-id'
        
        with patch.dict(os.environ, {'DDB_TABLE_NAME': 'ErasmusSBOMAnalysisCache'}):
            response = lambda_handler(event, context)
        
        assert response['statusCode'] == 200

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
