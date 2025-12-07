import json
import os
import logging
import boto3
import requests
import yaml
from datetime import datetime

# ----- Logging---------------
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# --- AWS Clients
s3 = boto3.client("s3")

# --- Environment Variables -----

API_KEY = os.environ.get("API_KEY")
BUCKET_NAME = os.environ.get("BUCKET_NAME")


def load_config():
    """Load YAML file packaged along with Lambda code"""
    config_path = os.path.join(os.path.dirname(__file__), "endpoints.yml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def lambda_handler(event, context):
    logger.info("Lambda triggered: Football API ingestion started")

    if not API_KEY or not BUCKET_NAME:
        raise Exception("API_KEY or BUCKET_NAME not set")

    cfg = load_config()
    base_url = cfg["base_url"]
    league = cfg["league"]
    endpoints = cfg["endpoints"]

    today = datetime.utcnow().strftime("%Y-%m-%d")
    headers = {"X-Auth-Token": API_KEY}

    for endpoint_name, path in endpoints.items():
        url = base_url + path
        logger.info(f"Calling API: {endpoint_name} -> {url}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Success:{endpoint_name} retrieved")
        except Exception as e:
            logger.error(f"Error fetching {endpoint_name}: {e}")
            continue

        # Build S3 object key (path inside bucket)
        key = f"raw/league={league}/date={today}/{endpoint_name}.json"

        try:
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=key,
                Body=json.dumps(data),
                ContentType="application/json",
            )
            logger.info(f"Uploaded to S3://{BUCKET_NAME}/{key}")
        except Exception as e:
            logger.error(f"Upload failed for {endpoint_name}: {e}")

    logger.info("Lambda completed")
    return {"statusCode": 200, "body": json.dumps({"status": "completed"})}
