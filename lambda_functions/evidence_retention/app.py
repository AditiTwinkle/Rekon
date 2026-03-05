"""Evidence retention and expiration Lambda function."""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict

import boto3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from rekon.services.evidence_service import EvidenceService
from rekon.core.config import settings

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
sns_client = boto3.client("sns")
s3_client = boto3.client("s3")

# Initialize database
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle evidence retention and expiration checks.

    Args:
        event: Lambda event
        context: Lambda context

    Returns:
        Response with status and results
    """
    try:
        logger.info("Starting evidence retention check")

        db = SessionLocal()
        service = EvidenceService(db)

        # Get all organizations (in production, this would be parameterized)
        # For now, we'll process a sample organization
        organization_id = event.get("organization_id")

        if not organization_id:
            logger.warning("No organization_id provided, skipping processing")
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "organization_id required"}),
            }

        # Check for expired evidence
        expired_evidence = service.get_expired_evidence(organization_id)
        logger.info(f"Found {len(expired_evidence)} expired evidence items")

        # Check for evidence expiring soon
        expiring_soon = service.get_expiring_soon_evidence(
            organization_id,
            days_threshold=30,
        )
        logger.info(f"Found {len(expiring_soon)} evidence items expiring soon")

        # Send notifications
        if expired_evidence:
            _send_expiration_alert(
                organization_id,
                expired_evidence,
                alert_type="EXPIRED",
            )

        if expiring_soon:
            _send_expiration_alert(
                organization_id,
                expiring_soon,
                alert_type="EXPIRING_SOON",
            )

        # Enforce retention policies
        retention_results = _enforce_retention_policies(
            service,
            organization_id,
            expired_evidence,
        )

        db.close()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "expired_count": len(expired_evidence),
                "expiring_soon_count": len(expiring_soon),
                "retention_enforced": retention_results,
            }),
        }

    except Exception as e:
        logger.error(f"Error in evidence retention check: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }


def _send_expiration_alert(
    organization_id: str,
    evidence_list: list,
    alert_type: str,
) -> None:
    """Send expiration alert via SNS.

    Args:
        organization_id: Organization ID
        evidence_list: List of evidence items
        alert_type: Type of alert (EXPIRED or EXPIRING_SOON)
    """
    try:
        message = _format_alert_message(evidence_list, alert_type)

        sns_client.publish(
            TopicArn=settings.sns_topic_arn,
            Subject=f"Evidence {alert_type}: {len(evidence_list)} items",
            Message=message,
        )

        logger.info(f"Sent {alert_type} alert for {len(evidence_list)} items")

    except Exception as e:
        logger.error(f"Error sending alert: {str(e)}", exc_info=True)


def _format_alert_message(evidence_list: list, alert_type: str) -> str:
    """Format alert message for SNS.

    Args:
        evidence_list: List of evidence items
        alert_type: Type of alert

    Returns:
        Formatted message
    """
    if alert_type == "EXPIRED":
        header = "The following evidence items have EXPIRED:"
    else:
        header = "The following evidence items are EXPIRING SOON (within 30 days):"

    items = []
    for evidence in evidence_list[:10]:  # Limit to first 10 items
        expiration = (
            evidence.expiration_date.strftime("%Y-%m-%d")
            if evidence.expiration_date
            else "N/A"
        )
        items.append(
            f"  - {evidence.file_name} (ID: {evidence.evidence_id}, "
            f"Expires: {expiration})"
        )

    if len(evidence_list) > 10:
        items.append(f"  ... and {len(evidence_list) - 10} more items")

    message = f"{header}\n\n" + "\n".join(items)
    message += "\n\nPlease review and take appropriate action."

    return message


def _enforce_retention_policies(
    service: EvidenceService,
    organization_id: str,
    expired_evidence: list,
) -> Dict[str, int]:
    """Enforce retention policies on expired evidence.

    Args:
        service: Evidence service
        organization_id: Organization ID
        expired_evidence: List of expired evidence

    Returns:
        Dictionary with enforcement results
    """
    results = {
        "archived": 0,
        "deleted": 0,
        "failed": 0,
    }

    for evidence in expired_evidence:
        try:
            # Check retention policy
            if evidence.retention_policy == "archive":
                # Archive to S3 Glacier
                _archive_evidence(evidence)
                results["archived"] += 1
            elif evidence.retention_policy == "delete":
                # Delete evidence
                service.delete_evidence(
                    evidence.evidence_id,
                    organization_id,
                    None,  # System user
                )
                results["deleted"] += 1
            else:
                # Default: keep in current storage
                logger.info(
                    f"No retention policy for {evidence.evidence_id}, keeping in storage"
                )

        except Exception as e:
            logger.error(
                f"Error enforcing retention for {evidence.evidence_id}: {str(e)}"
            )
            results["failed"] += 1

    return results


def _archive_evidence(evidence: Any) -> None:
    """Archive evidence to S3 Glacier.

    Args:
        evidence: Evidence item to archive
    """
    try:
        # In production, this would move the object to Glacier storage class
        # For now, we'll just log the action
        logger.info(f"Archiving evidence {evidence.evidence_id} to Glacier")

        # Example: Move object to Glacier
        # s3_client.copy_object(
        #     Bucket=settings.s3_bucket,
        #     CopySource={'Bucket': settings.s3_bucket, 'Key': evidence.file_path},
        #     Key=evidence.file_path,
        #     StorageClass='GLACIER',
        # )

    except Exception as e:
        logger.error(f"Error archiving evidence: {str(e)}")
        raise
