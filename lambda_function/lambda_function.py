import json
import boto3
import urllib.parse
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Table name
DDB_TABLE_NAME = "ErasmusSBOMAnalysisCache"

# OFAC mappings
OFAC_COUNTRIES = {
    'cuba': 'Cuba', 'iran': 'Iran', 'north korea': 'North Korea', 'dprk': 'North Korea',
    'syria': 'Syria', 'venezuela': 'Venezuela', 'russia': 'Russia', 'belarus': 'Belarus',
    'myanmar': 'Myanmar', 'burma': 'Myanmar', 'crimea': 'Crimea Region',
    'donetsk': 'Donetsk Region', 'luhansk': 'Luhansk Region'
}

DOMAIN_COUNTRY_MAPPING = {
    'ir': 'Iran', 'cu': 'Cuba', 'kp': 'North Korea', 'sy': 'Syria',
    've': 'Venezuela', 'ru': 'Russia', 'by': 'Belarus', 'mm': 'Myanmar'
}

def extract_domain_from_email(email):
    if not email or '@' not in email:
        return None
    try:
        return email.split('@')[1].lower()
    except:
        return None

def check_domain_for_ofac_risk(domain):
    if not domain:
        return None, 0.0
    tld = domain.split('.')[-1].lower()
    if tld in DOMAIN_COUNTRY_MAPPING:
        return DOMAIN_COUNTRY_MAPPING[tld], 0.8
    for keyword, country in OFAC_COUNTRIES.items():
        if keyword in domain:
            return country, 0.6
    return None, 0.0

def analyze_ofac(sbom_data):
    results = {
        "analysis_timestamp": datetime.utcnow().isoformat(),
        "components_analyzed": 0,
        "pypi_components": 0,
        "ofac_risks": []
    }

    components = sbom_data.get('components', [])
    results["components_analyzed"] = len(components)

    for component in components:
        name = component.get('name', '')
        version = component.get('version', '')
        purl = component.get('purl', '')

        if not purl.startswith('pkg:pypi/'):
            continue
        results["pypi_components"] += 1

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
                risk_info["origin_confidence"] = 0.9

        for label, email in [('author_email', author_email), ('maintainer_email', maintainer_email)]:
            domain = extract_domain_from_email(email)
            country, confidence = check_domain_for_ofac_risk(domain)
            if country:
                risk_info[f"{label}_domain"] = domain
                risk_info[f"{label}_country"] = country
                risk_info[f"{label}_confidence"] = confidence

        if risk_info:
            results["ofac_risks"].append({
                "name": name,
                "version": version,
                "purl": purl,
                "risk_factors": risk_info
            })

    results["summary"] = {
        "total_components": results["components_analyzed"],
        "pypi_components": results["pypi_components"],
        "ofac_risk_components": len(results["ofac_risks"]),
        "risk_level": "HIGH" if results["ofac_risks"] else "LOW"
    }

    return results

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        if 'Records' in event:
            bucket = event['Records'][0]['s3']['bucket']['name']
            key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
        elif 'detail' in event and 'bucket' in event['detail'] and 'object' in event['detail']:
            bucket = event['detail']['bucket']['name']
            key = event['detail']['object']['key']
        else:
            logger.error("Unsupported event format")
            return {'statusCode': 400, 'body': json.dumps('Unsupported event format')}

        if not key.startswith('sboms/') or not key.endswith('.json'):
            logger.info(f"Skipping non-SBOM file: {key}")
            return {'statusCode': 200, 'body': json.dumps('Not a SBOM file, skipping')}

        logger.info(f"Processing SBOM from {bucket}/{key}")

        response = s3_client.get_object(Bucket=bucket, Key=key)
        sbom_data = json.loads(response['Body'].read().decode('utf-8'))

        analysis_results = analyze_ofac(sbom_data)

        analysis_results["metadata"] = {
            "source_file": key,
            "analysis_time_utc": datetime.utcnow().isoformat(),
            "lambda_version": "v1.0.0"
        }

        file_name = key.split('/')[-1]
        output_key = f"analysis/{file_name.replace('.json', '_analysis.json')}"
        s3_client.put_object(
            Bucket=bucket,
            Key=output_key,
            Body=json.dumps(analysis_results, indent=2),
            ContentType='application/json'
        )

        try:
            table = dynamodb.Table(DDB_TABLE_NAME)
            table.put_item(Item={
                'sbom_id': str(file_name),
                'timestamp': datetime.utcnow().isoformat(),
                'summary': analysis_results["summary"],
                'output_key': output_key
            })
        except Exception as ddb_err:
            logger.warning(f"DynamoDB insert skipped or failed: {str(ddb_err)}")

        logger.info(f"Analysis complete. Saved to {output_key}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'SBOM analysis complete',
                'bucket': bucket,
                'input_key': key,
                'output_key': output_key,
                'summary': analysis_results["summary"]
            })
        }

    except Exception as e:
        logger.error(f"Lambda error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }