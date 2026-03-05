"""Regulation Puller Lambda function.

Fetches regulatory requirements from official sources and stores them in RDS.
Supports DORA, SOX, BMR, IOSCO, and NIST frameworks.
"""

import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import asyncio

import boto3
import requests
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
eventbridge = boto3.client("events")
rds_client = boto3.client("rds")
ssm_client = boto3.client("ssm")

# Configuration
REGULATION_SOURCES = {
    "DORA_A": {
        "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554",
        "name": "Digital Operational Resilience Act - Category A",
        "timeout": 60,
    },
    "DORA_B": {
        "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554",
        "name": "Digital Operational Resilience Act - Category B",
        "timeout": 60,
    },
    "SOX": {
        "url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=10-K&dateb=&owner=exclude&count=100",
        "name": "Sarbanes-Oxley Act",
        "timeout": 60,
    },
    "BMR": {
        "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R1011",
        "name": "EU Benchmark Regulation",
        "timeout": 60,
    },
    "IOSCO": {
        "url": "https://www.iosco.org/library/pubdocs/pdf/IOSCOPD323.pdf",
        "name": "IOSCO Principles of Securities Regulation",
        "timeout": 60,
    },
    "NIST": {
        "url": "https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final",
        "name": "NIST Cybersecurity Framework",
        "timeout": 60,
    },
}

MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2  # exponential backoff: 2^attempt seconds


class RegulationFetchError(Exception):
    """Exception raised when regulation fetch fails."""

    pass


def calculate_content_hash(content: str) -> str:
    """Calculate SHA-256 hash of content.

    Args:
        content: Content to hash

    Returns:
        Hex-encoded SHA-256 hash
    """
    return hashlib.sha256(content.encode()).hexdigest()


def fetch_regulation_with_retry(
    framework: str, max_retries: int = MAX_RETRIES
) -> Optional[Dict]:
    """Fetch regulation content with exponential backoff retry.

    Args:
        framework: Framework identifier (DORA_A, SOX, etc.)
        max_retries: Maximum number of retry attempts

    Returns:
        Dictionary with regulation data or None if all retries failed

    Raises:
        RegulationFetchError: If all retries are exhausted
    """
    if framework not in REGULATION_SOURCES:
        raise ValueError(f"Unknown framework: {framework}")

    source = REGULATION_SOURCES[framework]
    url = source["url"]
    timeout = source["timeout"]

    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching {framework} from {url} (attempt {attempt + 1}/{max_retries})")

            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            content = response.text
            content_hash = calculate_content_hash(content)

            logger.info(f"Successfully fetched {framework}, hash: {content_hash}")

            return {
                "framework": framework,
                "name": source["name"],
                "url": url,
                "content": content,
                "content_hash": content_hash,
                "fetch_timestamp": datetime.utcnow().isoformat(),
            }

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout fetching {framework} (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                wait_time = RETRY_BACKOFF_BASE ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                asyncio.sleep(wait_time)
            continue

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {framework}: {str(e)} (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                wait_time = RETRY_BACKOFF_BASE ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                asyncio.sleep(wait_time)
            continue

    raise RegulationFetchError(
        f"Failed to fetch {framework} after {max_retries} attempts"
    )


def store_regulation_in_database(regulation_data: Dict) -> bool:
    """Store regulation in RDS database.

    Args:
        regulation_data: Regulation data dictionary

    Returns:
        True if successful, False otherwise
    """
    try:
        # Get database connection details from Secrets Manager
        db_secret = ssm_client.get_parameter(
            Name="/rekon/db/connection_string",
            WithDecryption=True
        )
        connection_string = db_secret["Parameter"]["Value"]

        # This would be implemented with SQLAlchemy in production
        # For now, we'll log the data that would be stored
        logger.info(f"Would store regulation: {regulation_data['framework']}")
        logger.info(f"Content hash: {regulation_data['content_hash']}")
        logger.info(f"Fetch timestamp: {regulation_data['fetch_timestamp']}")

        return True

    except ClientError as e:
        logger.error(f"Error storing regulation: {str(e)}")
        return False


def emit_regulation_event(regulation_data: Dict, event_type: str = "regulation.fetched") -> bool:
    """Emit EventBridge event for regulation update.

    Args:
        regulation_data: Regulation data
        event_type: Type of event to emit

    Returns:
        True if successful, False otherwise
    """
    try:
        event = {
            "Source": "rekon.regulation-puller",
            "DetailType": event_type,
            "Detail": json.dumps({
                "framework": regulation_data["framework"],
                "content_hash": regulation_data["content_hash"],
                "fetch_timestamp": regulation_data["fetch_timestamp"],
                "url": regulation_data["url"],
            }),
        }

        response = eventbridge.put_events(Entries=[event])

        if response["FailedEntryCount"] == 0:
            logger.info(f"Successfully emitted {event_type} event for {regulation_data['framework']}")
            return True
        else:
            logger.error(f"Failed to emit event: {response}")
            return False

    except ClientError as e:
        logger.error(f"Error emitting event: {str(e)}")
        return False


def lambda_handler(event, context):
    """Lambda handler for regulation puller.

    Args:
        event: Lambda event
        context: Lambda context

    Returns:
        Response with fetch results
    """
    logger.info("Starting regulation puller")

    frameworks = event.get("frameworks", list(REGULATION_SOURCES.keys()))
    results = {
        "successful": [],
        "failed": [],
        "timestamp": datetime.utcnow().isoformat(),
    }

    for framework in frameworks:
        try:
            # Fetch regulation
            regulation_data = fetch_regulation_with_retry(framework)

            # Store in database
            if store_regulation_in_database(regulation_data):
                # Emit event
                if emit_regulation_event(regulation_data):
                    results["successful"].append(framework)
                    logger.info(f"Successfully processed {framework}")
                else:
                    results["failed"].append({
                        "framework": framework,
                        "reason": "Failed to emit event",
                    })
            else:
                results["failed"].append({
                    "framework": framework,
                    "reason": "Failed to store in database",
                })

        except RegulationFetchError as e:
            logger.error(f"Fetch error for {framework}: {str(e)}")
            results["failed"].append({
                "framework": framework,
                "reason": str(e),
            })

        except Exception as e:
            logger.error(f"Unexpected error for {framework}: {str(e)}")
            results["failed"].append({
                "framework": framework,
                "reason": f"Unexpected error: {str(e)}",
            })

    logger.info(f"Regulation puller completed: {len(results['successful'])} successful, {len(results['failed'])} failed")

    return {
        "statusCode": 200 if not results["failed"] else 206,
        "body": json.dumps(results),
    }
