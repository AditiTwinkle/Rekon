"""Delta Analyzer Lambda function."""

import json
import logging
import os
from datetime import datetime
from uuid import UUID

import boto3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from rekon.services.delta_analyzer_service import DeltaAnalyzerService

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
eventbridge = boto3.client("events")

# Database setup
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def lambda_handler(event, context):
    """Lambda handler for delta analysis.

    Args:
        event: Lambda event
        context: Lambda context

    Returns:
        Response with analysis results
    """
    logger.info(f"Delta Analyzer Lambda invoked with event: {json.dumps(event)}")

    try:
        # Extract parameters
        organization_id = event.get("organization_id")
        user_id = event.get("user_id", "system")

        if not organization_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "organization_id is required"}),
            }

        # Create database session
        db = SessionLocal()

        try:
            # Perform delta analysis
            analyzer = DeltaAnalyzerService(db)
            analysis_result = analyzer.analyze_compliance_delta(
                UUID(organization_id),
                UUID(user_id),
            )

            # Add timestamp
            analysis_result["analysis_timestamp"] = datetime.utcnow().isoformat()

            # Emit EventBridge event for downstream processing
            _emit_analysis_event(analysis_result)

            logger.info(
                f"Delta analysis completed for organization {organization_id}"
            )

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "organization_id": organization_id,
                        "gaps_identified": len(analysis_result["gaps_identified"]),
                        "analysis_timestamp": analysis_result["analysis_timestamp"],
                    }
                ),
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in delta analysis: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }


def _emit_analysis_event(analysis_result: dict) -> None:
    """Emit EventBridge event for analysis completion.

    Args:
        analysis_result: Analysis result
    """
    try:
        eventbridge.put_events(
            Entries=[
                {
                    "Source": "rekon.delta-analyzer",
                    "DetailType": "DeltaAnalysisCompleted",
                    "Detail": json.dumps(
                        {
                            "organization_id": str(analysis_result["organization_id"]),
                            "gaps_identified": len(analysis_result["gaps_identified"]),
                            "analysis_timestamp": analysis_result["analysis_timestamp"],
                        }
                    ),
                }
            ]
        )
        logger.info("EventBridge event emitted for delta analysis completion")
    except Exception as e:
        logger.error(f"Failed to emit EventBridge event: {str(e)}")
