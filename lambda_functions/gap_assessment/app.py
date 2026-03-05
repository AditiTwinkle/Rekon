"""Gap Assessment Lambda function."""

import json
import logging
import os
from uuid import UUID

import boto3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from rekon.services.gap_assessment_service import GapAssessmentService

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Database setup
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def lambda_handler(event, context):
    """Lambda handler for gap assessment.

    Args:
        event: Lambda event
        context: Lambda context

    Returns:
        Response with assessment data
    """
    logger.info(f"Gap Assessment Lambda invoked with event: {json.dumps(event)}")

    try:
        action = event.get("action")
        organization_id = event.get("organization_id")
        gap_id = event.get("gap_id")
        assessment_id = event.get("assessment_id")

        # Create database session
        db = SessionLocal()

        try:
            service = GapAssessmentService(db)

            if action == "start":
                if not organization_id or not gap_id:
                    return {
                        "statusCode": 400,
                        "body": json.dumps(
                            {"error": "organization_id and gap_id are required"}
                        ),
                    }

                result = service.start_assessment(
                    UUID(organization_id),
                    UUID(gap_id),
                )

                return {
                    "statusCode": 200,
                    "body": json.dumps(result, default=str),
                }

            elif action == "submit_response":
                if not assessment_id:
                    return {
                        "statusCode": 400,
                        "body": json.dumps({"error": "assessment_id is required"}),
                    }

                question_id = event.get("question_id")
                response_text = event.get("response_text")
                confidence_level = event.get("confidence_level", 0.8)

                result = service.submit_response(
                    UUID(assessment_id),
                    UUID(question_id),
                    response_text,
                    confidence_level,
                )

                return {
                    "statusCode": 200,
                    "body": json.dumps(result, default=str),
                }

            elif action == "pause":
                if not assessment_id:
                    return {
                        "statusCode": 400,
                        "body": json.dumps({"error": "assessment_id is required"}),
                    }

                result = service.pause_assessment(UUID(assessment_id))

                return {
                    "statusCode": 200,
                    "body": json.dumps(result, default=str),
                }

            elif action == "resume":
                if not assessment_id:
                    return {
                        "statusCode": 400,
                        "body": json.dumps({"error": "assessment_id is required"}),
                    }

                result = service.resume_assessment(UUID(assessment_id))

                return {
                    "statusCode": 200,
                    "body": json.dumps(result, default=str),
                }

            elif action == "summary":
                if not assessment_id:
                    return {
                        "statusCode": 400,
                        "body": json.dumps({"error": "assessment_id is required"}),
                    }

                result = service.get_assessment_summary(UUID(assessment_id))

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
        logger.error(f"Error in gap assessment: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }
