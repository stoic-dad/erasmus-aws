import json
import boto3
import urllib.parse
import logging
import re
import requests
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from packaging import version

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Environment variables
import os
DDB_TABLE_NAME = os.environ.get('DDB_TABLE_NAME', 'ErasmusSBOMAnalysisCache')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', '')
NVD_API_KEY = os.environ.get('NVD_API_KEY', '')  # Optional: for higher rate limits

# OFAC mappings - Enhanced with more comprehensive coverage
OFAC_COUNTRIES = {
    'cuba': 'Cuba', 'iran': 'Iran', 'tehran': 'Iran', 'north korea': 'North Korea', 'dprk': 'North Korea',
    'syria': 'Syria', 'venezuela': 'Venezuela', 'russia': 'Russia', 'belarus': 'Belarus',
    'myanmar': 'Myanmar', 'burma': 'Myanmar', 'crimea': 'Crimea Region',
    'donetsk': 'Donetsk Region', 'luhansk': 'Luhansk Region', 'afghanistan': 'Afghanistan',
    'balkans': 'Western Balkans', 'lebanon': 'Lebanon', 'libya': 'Libya',
    'somalia': 'Somalia', 'sudan': 'Sudan', 'yemen': 'Yemen', 'zimbabwe': 'Zimbabwe'
}

DOMAIN_COUNTRY_MAPPING = {
    'ir': 'Iran', 'cu': 'Cuba', 'kp': 'North Korea', 'sy': 'Syria',
    've': 'Venezuela', 'ru': 'Russia', 'by': 'Belarus', 'mm': 'Myanmar',
    'af': 'Afghanistan', 'lb': 'Lebanon', 'ly': 'Libya', 'so': 'Somalia',
    'sd': 'Sudan', 'ye': 'Yemen', 'zw': 'Zimbabwe'
}

# Risk scoring weights
RISK_WEIGHTS = {
    'domain_match': 0.8,
    'keyword_match': 0.6,
    'origin_explicit': 0.9,
    'maintainer_email': 0.7,
    'author_email': 0.7,
    'critical_cve': 1.0,
    'high_cve': 0.8
}

# CVE Severity mappings
CVE_SEVERITY_SCORES = {
    'CRITICAL': 1.0,
    'HIGH': 0.8,
    'MEDIUM': 0.5,
    'LOW': 0.2,
    'NONE': 0.0
}

def get_cve_data_for_package(package_name: str, package_version: str, ecosystem: str) -> List[Dict]:
    """
    Fetch CVE data for a specific package from NVD API.
    Returns list of critical and high severity CVEs.
    """
    try:
        # Construct CPE name based on ecosystem
        cpe_vendor = {
            'pypi': 'python',
            'npm': 'nodejs', 
            'maven': 'apache',
            'nuget': 'microsoft'
        }.get(ecosystem, ecosystem)
        
        # Use NVD REST API v2
        base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        headers = {
            'User-Agent': 'Erasmus-SBOM-Analyzer/1.0'
        }
        
        if NVD_API_KEY:
            headers['apiKey'] = NVD_API_KEY
            
        # Search for CVEs related to the package
        params = {
            'keywordSearch': f"{package_name}",
            'resultsPerPage': 50,
            'cvssV3Severity': 'HIGH,CRITICAL'  # Only get critical/high CVEs
        }
        
        response = requests.get(base_url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            cves = []
            
            for vulnerability in data.get('vulnerabilities', []):
                cve = vulnerability.get('cve', {})
                cve_id = cve.get('id', '')
                
                # Get CVSS scores
                metrics = cve.get('metrics', {})
                cvss_score = 0.0
                severity = 'UNKNOWN'
                
                # Try CVSS v3.1 first, then v3.0, then v2
                for cvss_version in ['cvssMetricV31', 'cvssMetricV30', 'cvssMetricV2']:
                    if cvss_version in metrics and metrics[cvss_version]:
                        metric = metrics[cvss_version][0]
                        if 'cvssData' in metric:
                            cvss_score = metric['cvssData'].get('baseScore', 0.0)
                            severity = metric['cvssData'].get('baseSeverity', 'UNKNOWN')
                            break
                
                # Only include CRITICAL and HIGH severity CVEs
                if severity in ['CRITICAL', 'HIGH']:
                    description = ''
                    descriptions = cve.get('descriptions', [])
                    for desc in descriptions:
                        if desc.get('lang') == 'en':
                            description = desc.get('value', '')
                            break
                    
                    cves.append({
                        'cve_id': cve_id,
                        'cvss_score': cvss_score,
                        'severity': severity,
                        'description': description[:200] + '...' if len(description) > 200 else description,
                        'published_date': cve.get('published', ''),
                        'last_modified': cve.get('lastModified', '')
                    })
            
            return sorted(cves, key=lambda x: x['cvss_score'], reverse=True)[:10]  # Top 10 highest scoring CVEs
            
    except Exception as e:
        logger.warning(f"Failed to fetch CVE data for {package_name}: {str(e)}")
        return []
    
    return []

def calculate_dependency_depth(components: List[Dict]) -> Dict:
    """
    Calculate dependency depth and hierarchy information from SBOM components.
    """
    depth_info = {
        'max_depth': 0,
        'depth_distribution': {},
        'total_dependencies': len(components),
        'direct_dependencies': 0,
        'transitive_dependencies': 0,
        'dependency_tree': {}
    }
    
    try:
        # Build dependency relationships
        component_map = {}
        dependency_graph = {}
        
        for component in components:
            purl = component.get('purl', '')
            name = component.get('name', '')
            component_map[purl] = component
            dependency_graph[purl] = {
                'component': component,
                'dependencies': [],
                'dependents': [],
                'depth': 0
            }
        
        # Analyze dependency relationships if present
        for component in components:
            purl = component.get('purl', '')
            dependencies = component.get('dependencies', [])
            
            for dep in dependencies:
                dep_ref = dep.get('ref', '')
                if dep_ref in dependency_graph:
                    dependency_graph[purl]['dependencies'].append(dep_ref)
                    dependency_graph[dep_ref]['dependents'].append(purl)
        
        # Calculate depths using BFS from root components (those with no dependents)
        root_components = [purl for purl, info in dependency_graph.items() 
                          if not info['dependents']]
        
        if not root_components:
            # If no clear hierarchy, treat first level as direct dependencies
            depth_info['direct_dependencies'] = min(len(components), 20)
            depth_info['transitive_dependencies'] = max(0, len(components) - 20)
            depth_info['max_depth'] = 1 if components else 0
            depth_info['depth_distribution'] = {'1': len(components)} if components else {}
        else:
            # Calculate actual depths
            visited = set()
            queue = [(purl, 0) for purl in root_components]
            
            while queue:
                current_purl, depth = queue.pop(0)
                if current_purl in visited:
                    continue
                    
                visited.add(current_purl)
                dependency_graph[current_purl]['depth'] = depth
                depth_info['max_depth'] = max(depth_info['max_depth'], depth)
                
                # Count by depth
                depth_str = str(depth)
                depth_info['depth_distribution'][depth_str] = depth_info['depth_distribution'].get(depth_str, 0) + 1
                
                # Add dependencies to queue
                for dep_purl in dependency_graph[current_purl]['dependencies']:
                    if dep_purl not in visited:
                        queue.append((dep_purl, depth + 1))
            
            # Count direct vs transitive
            depth_info['direct_dependencies'] = depth_info['depth_distribution'].get('0', 0)
            depth_info['transitive_dependencies'] = len(components) - depth_info['direct_dependencies']
        
        # Create simplified dependency tree for visualization
        depth_info['dependency_tree'] = {
            str(i): [] for i in range(depth_info['max_depth'] + 1)
        }
        
        for purl, info in dependency_graph.items():
            depth_str = str(info['depth'])
            component_name = info['component'].get('name', 'unknown')
            if depth_str in depth_info['dependency_tree']:
                depth_info['dependency_tree'][depth_str].append({
                    'name': component_name,
                    'purl': purl,
                    'dependencies_count': len(info['dependencies'])
                })
        
    except Exception as e:
        logger.warning(f"Failed to calculate dependency depth: {str(e)}")
    
    return depth_info

def extract_domain_from_email(email: str) -> Optional[str]:
    """Extract domain from email address with validation."""
    if not email or '@' not in email:
        return None
    try:
        parts = email.split('@')
        if len(parts) != 2 or not parts[0] or not parts[1]:
            return None
        domain = parts[1].lower().strip()
        # Basic domain validation
        if re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$', domain):
            return domain
        return None
    except (IndexError, AttributeError):
        return None

def check_domain_for_ofac_risk(domain: str) -> Tuple[Optional[str], float]:
    """Enhanced domain risk checking with better scoring."""
    if not domain:
        return None, 0.0
    
    # Check TLD mapping first (highest confidence)
    tld = domain.split('.')[-1].lower()
    if tld in DOMAIN_COUNTRY_MAPPING:
        return DOMAIN_COUNTRY_MAPPING[tld], RISK_WEIGHTS['domain_match']
    
    # Check for keyword matches in domain
    domain_lower = domain.lower()
    for keyword, country in OFAC_COUNTRIES.items():
        if keyword in domain_lower:
            return country, RISK_WEIGHTS['keyword_match']
    
    return None, 0.0

def calculate_component_risk_score(risk_factors: Dict) -> float:
    """Calculate overall risk score for a component."""
    total_score = 0.0
    max_possible = 1.0
    
    for factor, details in risk_factors.items():
        if isinstance(details, dict) and 'confidence' in details:
            total_score += details['confidence']
        elif factor.endswith('_confidence'):
            total_score += risk_factors[factor]
    
    return min(total_score, max_possible)

def analyze_ofac(sbom_data: Dict) -> Dict:
    """Enhanced OFAC analysis with CVE data and dependency depth analysis."""
    results = {
        "analysis_timestamp": datetime.utcnow().isoformat(),
        "components_analyzed": 0,
        "pypi_components": 0,
        "npm_components": 0,
        "maven_components": 0,
        "nuget_components": 0,
        "other_components": 0,
        "ofac_risks": [],
        "cve_analysis": {
            "critical_cves": [],
            "high_cves": [],
            "total_cves_found": 0,
            "components_with_cves": 0
        },
        "dependency_analysis": {},
        "executive_summary": {}
    }

    components = sbom_data.get('components', [])
    results["components_analyzed"] = len(components)

    # Calculate dependency depth
    results["dependency_analysis"] = calculate_dependency_depth(components)

    # Track components with vulnerabilities
    vulnerable_components = []
    total_cves = 0

    for component in components:
        name = component.get('name', '')
        version = component.get('version', '')
        purl = component.get('purl', '')

        # Determine ecosystem
        ecosystem = 'unknown'
        if purl.startswith('pkg:pypi/'):
            ecosystem = 'pypi'
            results["pypi_components"] += 1
        elif purl.startswith('pkg:npm/'):
            ecosystem = 'npm'
            results["npm_components"] += 1
        elif purl.startswith('pkg:maven/'):
            ecosystem = 'maven'
            results["maven_components"] += 1
        elif purl.startswith('pkg:nuget/'):
            ecosystem = 'nuget'
            results["nuget_components"] += 1
        else:
            ecosystem = 'other'
            results["other_components"] += 1

        # OFAC Risk Analysis (existing logic)
        author_email = maintainer_email = None
        risk_info = {}
        properties = component.get('properties', [])

        for prop in properties:
            if prop.get('name') == 'author_email':
                author_email = prop.get('value')
            elif prop.get('name') == 'maintainer_email':
                maintainer_email = prop.get('value')
            elif prop.get('name') == 'origin' and prop.get('value') in OFAC_COUNTRIES.values():
                risk_info["origin_country"] = prop.get('value')
                risk_info["origin_confidence"] = RISK_WEIGHTS['origin_explicit']

        for label, email in [('author_email', author_email), ('maintainer_email', maintainer_email)]:
            domain = extract_domain_from_email(email)
            country, confidence = check_domain_for_ofac_risk(domain)
            if country:
                risk_info[f"{label}_domain"] = domain
                risk_info[f"{label}_country"] = country
                risk_info[f"{label}_confidence"] = confidence

        # CVE Analysis for each component
        component_cves = []
        if ecosystem in ['pypi', 'npm', 'maven', 'nuget'] and name and version:
            component_cves = get_cve_data_for_package(name, version, ecosystem)
            
            if component_cves:
                vulnerable_components.append({
                    'name': name,
                    'version': version,
                    'ecosystem': ecosystem,
                    'cve_count': len(component_cves),
                    'highest_cvss': max([cve['cvss_score'] for cve in component_cves], default=0.0),
                    'critical_count': len([cve for cve in component_cves if cve['severity'] == 'CRITICAL']),
                    'high_count': len([cve for cve in component_cves if cve['severity'] == 'HIGH'])
                })
                
                total_cves += len(component_cves)
                
                # Add CVE risk to component risk assessment
                max_cve_score = max([cve['cvss_score'] for cve in component_cves], default=0.0)
                if max_cve_score >= 9.0:  # Critical
                    risk_info["cve_risk"] = "CRITICAL"
                    risk_info["cve_confidence"] = RISK_WEIGHTS['critical_cve']
                elif max_cve_score >= 7.0:  # High
                    risk_info["cve_risk"] = "HIGH"
                    risk_info["cve_confidence"] = RISK_WEIGHTS['high_cve']
                
                # Categorize CVEs
                for cve in component_cves:
                    cve_entry = {
                        "component": name,
                        "version": version,
                        "ecosystem": ecosystem,
                        **cve
                    }
                    if cve['severity'] == 'CRITICAL':
                        results["cve_analysis"]["critical_cves"].append(cve_entry)
                    elif cve['severity'] == 'HIGH':
                        results["cve_analysis"]["high_cves"].append(cve_entry)

        # Calculate overall component risk score
        component_risk_score = calculate_component_risk_score(risk_info)

        # Add to OFAC risks if any risk factors found
        if risk_info:
            risk_entry = {
                "name": name,
                "version": version,
                "purl": purl,
                "ecosystem": ecosystem,
                "risk_factors": risk_info,
                "risk_score": component_risk_score,
                "cves": component_cves[:5]  # Top 5 CVEs for this component
            }
            results["ofac_risks"].append(risk_entry)

    # Update CVE analysis summary
    results["cve_analysis"]["total_cves_found"] = total_cves
    results["cve_analysis"]["components_with_cves"] = len(vulnerable_components)
    results["cve_analysis"]["vulnerable_components"] = vulnerable_components[:20]  # Top 20 most vulnerable

    # Generate Executive Summary
    results["executive_summary"] = generate_executive_summary(results)

    # Generate overall risk assessment
    critical_issues = len(results["cve_analysis"]["critical_cves"])
    high_issues = len(results["cve_analysis"]["high_cves"]) + len(results["ofac_risks"])
    
    overall_risk = "LOW"
    if critical_issues > 0:
        overall_risk = "CRITICAL"
    elif high_issues > 0:
        overall_risk = "HIGH"
    elif results["cve_analysis"]["components_with_cves"] > 0:
        overall_risk = "MEDIUM"

    results["summary"] = {
        "total_components": results["components_analyzed"],
        "pypi_components": results["pypi_components"],
        "npm_components": results["npm_components"],
        "maven_components": results["maven_components"],
        "ofac_risk_components": len(results["ofac_risks"]),
        "vulnerable_components": results["cve_analysis"]["components_with_cves"],
        "critical_cves": len(results["cve_analysis"]["critical_cves"]),
        "high_cves": len(results["cve_analysis"]["high_cves"]),
        "max_dependency_depth": results["dependency_analysis"]["max_depth"],
        "overall_risk_level": overall_risk,
        "risk_level": overall_risk  # Add this for consistency
    }

    return results

def generate_executive_summary(analysis_results: Dict) -> Dict:
    """Generate executive summary and BLUF for leadership."""
    summary = analysis_results.get("summary", {})
    cve_analysis = analysis_results.get("cve_analysis", {})
    dependency_analysis = analysis_results.get("dependency_analysis", {})
    
    # BLUF (Bottom Line Up Front)
    critical_cves = cve_analysis.get("critical_cves", [])
    high_cves = cve_analysis.get("high_cves", [])
    ofac_risks = analysis_results.get("ofac_risks", [])
    
    # Risk assessment
    risk_indicators = []
    if critical_cves:
        risk_indicators.append(f"{len(critical_cves)} CRITICAL vulnerabilities")
    if high_cves:
        risk_indicators.append(f"{len(high_cves)} HIGH vulnerabilities") 
    if ofac_risks:
        risk_indicators.append(f"{len(ofac_risks)} OFAC compliance risks")
    
    # Generate BLUF
    if not risk_indicators:
        bluf = "✅ SBOM ANALYSIS: LOW RISK - No critical security issues identified."
        recommendation = "Proceed with deployment. Continue regular security monitoring."
        risk_level = "LOW"
    elif critical_cves:
        bluf = f"🚨 SBOM ANALYSIS: CRITICAL RISK - {len(critical_cves)} critical vulnerabilities require immediate attention."
        recommendation = "HALT DEPLOYMENT. Address critical vulnerabilities before proceeding."
        risk_level = "CRITICAL"
    elif high_cves or ofac_risks:
        bluf = f"⚠️ SBOM ANALYSIS: HIGH RISK - {len(risk_indicators)} significant issues identified."
        recommendation = "Review and remediate high-risk components before deployment."
        risk_level = "HIGH"
    else:
        bluf = "⚠️ SBOM ANALYSIS: MEDIUM RISK - Some vulnerabilities identified."
        recommendation = "Plan remediation activities and monitor for updates."
        risk_level = "MEDIUM"
    
    # Key metrics for executives
    total_components = summary.get("total_components", 0)
    vulnerable_percentage = (cve_analysis.get("components_with_cves", 0) / max(total_components, 1)) * 100
    
    # Top risks for executive attention
    top_risks = []
    
    # Add critical CVEs
    for cve in critical_cves[:3]:  # Top 3 critical
        top_risks.append({
            "type": "Critical Vulnerability",
            "component": cve.get("component", "Unknown"),
            "issue": f"CVE-{cve.get('cve_id', 'Unknown')} (CVSS: {cve.get('cvss_score', 'N/A')})",
            "impact": "System compromise, data breach risk"
        })
    
    # Add OFAC risks
    for risk in ofac_risks[:2]:  # Top 2 OFAC risks
        risk_factors = risk.get("risk_factors", {})
        country = risk_factors.get("origin_country") or risk_factors.get("author_email_country", "Unknown")
        top_risks.append({
            "type": "OFAC Compliance Risk", 
            "component": risk.get("name", "Unknown"),
            "issue": f"Component linked to {country}",
            "impact": "Regulatory compliance violation"
        })
    
    return {
        "bluf": bluf,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "key_metrics": {
            "total_components": total_components,
            "vulnerable_components": cve_analysis.get("components_with_cves", 0),
            "vulnerable_percentage": round(vulnerable_percentage, 1),
            "critical_issues": len(critical_cves),
            "high_issues": len(high_cves),
            "ofac_risks": len(ofac_risks),
            "dependency_depth": dependency_analysis.get("max_depth", 0),
            "direct_dependencies": dependency_analysis.get("direct_dependencies", 0),
            "transitive_dependencies": dependency_analysis.get("transitive_dependencies", 0)
        },
        "top_risks": top_risks[:5],  # Top 5 risks for executive attention
        "analysis_timestamp": analysis_results.get("analysis_timestamp", ""),
        "action_required": len(critical_cves) > 0 or len(ofac_risks) > 0
    }

def lambda_handler(event, context):
    """Enhanced Lambda handler with better error handling and validation."""
    start_time = datetime.utcnow()
    logger.info(f"Received event: {json.dumps(event, default=str)}")

    try:
        # Enhanced event parsing with multiple triggers support
        bucket = key = sbom_data = None
        is_api_gateway_request = False
        
        # Check for API Gateway request (direct SBOM analysis)
        if 'httpMethod' in event or ('requestContext' in event and 'http' in event['requestContext']):
            is_api_gateway_request = True
            logger.info("Processing API Gateway request")
            
            # Parse request body
            try:
                if 'body' in event:
                    body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
                    sbom_data = body.get('sbom')
                    
                    if not sbom_data:
                        return {
                            'statusCode': 400,
                            'headers': {
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Headers': 'Content-Type',
                                'Access-Control-Allow-Methods': 'POST, OPTIONS'
                            },
                            'body': json.dumps({'error': 'Missing sbom data in request body'})
                        }
                else:
                    return {
                        'statusCode': 400,
                        'headers': {
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Headers': 'Content-Type',
                            'Access-Control-Allow-Methods': 'POST, OPTIONS'
                        },
                        'body': json.dumps({'error': 'Missing request body'})
                    }
            except json.JSONDecodeError as e:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'POST, OPTIONS'
                    },
                    'body': json.dumps({'error': f'Invalid JSON in request body: {str(e)}'})
                }
        
        elif 'Records' in event and len(event['Records']) > 0:
            # S3 event trigger
            record = event['Records'][0]
            if 's3' in record:
                bucket = record['s3']['bucket']['name']
                key = urllib.parse.unquote_plus(record['s3']['object']['key'])
            else:
                logger.error("S3 record format not recognized")
                return {'statusCode': 400, 'body': json.dumps('Invalid S3 event format')}
        elif 'detail' in event:
            # EventBridge trigger
            if 'bucket' in event['detail'] and 'object' in event['detail']:
                bucket = event['detail']['bucket']['name']
                key = event['detail']['object']['key']
            else:
                logger.error("EventBridge event format not recognized")
                return {'statusCode': 400, 'body': json.dumps('Invalid EventBridge event format')}
        elif 'bucket' in event and 'key' in event:
            # Direct invocation
            bucket = event['bucket']
            key = event['key']
        else:
            logger.error(f"Unsupported event format: {json.dumps(event, default=str)}")
            return {'statusCode': 400, 'body': json.dumps('Unsupported event format')}

        # Handle API Gateway request (direct SBOM analysis)
        if is_api_gateway_request:
            # Validate SBOM format
            if 'components' not in sbom_data:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'POST, OPTIONS'
                    },
                    'body': json.dumps({'error': 'Invalid SBOM format: missing components field'})
                }

            # Perform analysis
            logger.info("Starting OFAC analysis via API Gateway...")
            analysis_results = analyze_ofac(sbom_data)

            # Enhanced metadata for API Gateway requests
            analysis_results["metadata"] = {
                "source": "api-gateway",
                "analysis_time_utc": datetime.utcnow().isoformat(),
                "processing_time_seconds": (datetime.utcnow() - start_time).total_seconds(),
                "lambda_version": "v2.0.0",
                "lambda_request_id": context.aws_request_id if context else "unknown"
            }

            # Return results directly for API Gateway
            total_processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"API Gateway analysis complete in {total_processing_time:.2f}s")

            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps(analysis_results, default=str)
            }

        # Handle S3-based processing
        # Validate inputs
        if not bucket or not key:
            logger.error("Missing bucket or key in event")
            return {'statusCode': 400, 'body': json.dumps('Missing bucket or key')}

        # Validate file format
        if not key.startswith('sboms/') or not key.endswith('.json'):
            logger.info(f"Skipping non-SBOM file: {key}")
            return {'statusCode': 200, 'body': json.dumps('Not a SBOM file, skipping')}

        logger.info(f"Processing SBOM from s3://{bucket}/{key}")

        # Enhanced S3 object retrieval with validation
        try:
            response = s3_client.get_object(Bucket=bucket, Key=key)
            content_length = response.get('ContentLength', 0)
            
            # Check file size (max 10MB for Lambda)
            if content_length > 10 * 1024 * 1024:
                logger.error(f"File too large: {content_length} bytes")
                return {'statusCode': 413, 'body': json.dumps('File too large')}
            
            sbom_content = response['Body'].read().decode('utf-8')
            sbom_data = json.loads(sbom_content)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {str(e)}")
            return {'statusCode': 400, 'body': json.dumps(f'Invalid JSON: {str(e)}')}
        except Exception as e:
            logger.error(f"Error reading S3 object: {str(e)}")
            return {'statusCode': 500, 'body': json.dumps(f'S3 read error: {str(e)}')}

        # Validate SBOM format
        if 'components' not in sbom_data:
            logger.error("Invalid SBOM format: missing 'components' field")
            return {'statusCode': 400, 'body': json.dumps('Invalid SBOM format')}

        # Perform analysis
        logger.info("Starting OFAC analysis...")
        analysis_results = analyze_ofac(sbom_data)

        # Enhanced metadata
        file_name = key.split('/')[-1]
        analysis_results["metadata"] = {
            "source_file": key,
            "source_bucket": bucket,
            "file_size_bytes": content_length,
            "analysis_time_utc": datetime.utcnow().isoformat(),
            "processing_time_seconds": (datetime.utcnow() - start_time).total_seconds(),
            "lambda_version": "v2.0.0",
            "lambda_request_id": context.aws_request_id if context else "unknown"
        }

        # Save results to S3 with enhanced naming
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_key = f"analysis/{file_name.replace('.json', f'_analysis_{timestamp}.json')}"
        
        try:
            s3_client.put_object(
                Bucket=bucket,
                Key=output_key,
                Body=json.dumps(analysis_results, indent=2, default=str),
                ContentType='application/json',
                Metadata={
                    'analysis-version': 'v2.0.0',
                    'source-file': file_name,
                    'risk-level': analysis_results["summary"]["risk_level"]
                }
            )
        except Exception as e:
            logger.error(f"Error saving analysis to S3: {str(e)}")
            return {'statusCode': 500, 'body': json.dumps(f'S3 write error: {str(e)}')}

        # Enhanced DynamoDB logging with error handling
        try:
            table = dynamodb.Table(DDB_TABLE_NAME)
            ddb_item = {
                'sbom_id': str(file_name),
                'timestamp': datetime.utcnow().isoformat(),
                'bucket': bucket,
                'source_key': key,
                'output_key': output_key,
                'summary': analysis_results["summary"],
                'processing_time_seconds': analysis_results["metadata"]["processing_time_seconds"],
                'lambda_request_id': analysis_results["metadata"]["lambda_request_id"]
            }
            table.put_item(Item=ddb_item)
            logger.info("Successfully logged to DynamoDB")
        except Exception as ddb_err:
            logger.warning(f"DynamoDB insert failed: {str(ddb_err)}")
            # Don't fail the entire process for DynamoDB issues

        total_processing_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"Analysis complete in {total_processing_time:.2f}s. Saved to {output_key}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'SBOM analysis complete',
                'bucket': bucket,
                'input_key': key,
                'output_key': output_key,
                'processing_time_seconds': total_processing_time,
                'summary': analysis_results["summary"],
                'metadata': analysis_results["metadata"]
            }, default=str)
        }

    except Exception as e:
        total_processing_time = (datetime.utcnow() - start_time).total_seconds()
        error_msg = f"Lambda error after {total_processing_time:.2f}s: {str(e)}"
        logger.error(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'processing_time_seconds': total_processing_time,
                'request_id': context.aws_request_id if context else "unknown"
            })
        }