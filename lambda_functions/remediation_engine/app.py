"""Remediation Engine Lambda function."""

import json
import logging
import os
from uuid import UUID

import boto3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from rekon.services.remediation_service import RemediationService
from rekon.domain.models.remediation import RemediationStepStatusEnum

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Database setup
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def lambda_handler(event, context):
    """Lambda handler for remediation engine.

    Args:
        event: Lambda event
        context: Lambda context

    Returns:
        Response with remediation data
    """
    logger.info(f"Remediation Engine Lambda invoked with event: {json.dumps(event)}")

    try:
        action = event.get("action")
        organization_id = event.get("organization_id")
        gap_id = event.get("gap_id")
        plan_id = event.get("plan_id")
        step_id = event.get("step_id")

        # Create database session
        db = SessionLocal()

        try:
            service = RemediationService(db)

            if action == "generate":
                if not organization_id or not gap_id:
                    return {
                        "statusCode": 400,
                        "body": json.dumps(
                            {"error": "organization_id and gap_id are required"}
                        ),
                    }

                result = service.generate_remediation_plan(
                    UUID(organization_id),
                    UUID(gap_id),
                )

                return {
                    "statusCode": 200,
                    "body": json.dumps(result, default=str),
                }

            elif action == "update_step":
                if not step_id:
                    return {
                        "statusCode": 400,
                        "body": json.dumps({"error": "step_id is required"}),
                    }

                status_str = event.get("status", "IN_PROGRESS")
                status = RemediationStepStatusEnum[status_str]

                result = service.update_step_status(UUID(step_id), status)

                return {
                    "statusCode": 200,
                    "body": json.dumps(result, default=str),
                }

            elif action == "progress":
                if not plan_id:
                    return {
                        "statusCode": 400,
                        "body": json.dumps({"error": "plan_id is required"}),
                    }

                result = service.get_remediation_progress(UUID(plan_id))

                return {
                    "statusCode": 200,
                    "body": json.dumps(result, default=str),
                }

            else:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": f"Unknown action: {action}"}),
                }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in remediation engine: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }
