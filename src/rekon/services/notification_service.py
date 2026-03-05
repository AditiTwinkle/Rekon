"""Notification service for compliance alerts."""

import logging
import json
from typing import List, Dict

import boto3

logger = logging.getLogger(__name__)

sns_client = boto3.client("sns")


class NotificationService:
    """Service for sending notifications."""

    def __init__(self, sns_topic_arn: str = None):
        """Initialize notification service.

        Args:
            sns_topic_arn: SNS topic ARN for notifications
        """
        self.sns_topic_arn = sns_topic_arn

    def notify_regulation_update(
        self,
        framework: str,
        change_summary: str,
    ) -> bool:
        """Notify stakeholders of regulation update.

        Args:
            framework: Framework identifier
            change_summary: Summary of changes

        Returns:
            True if successful, False otherwise
        """
        if not self.sns_topic_arn:
            logger.warning("SNS topic ARN not configured")
            return False

        try:
            message = {
                "framework": framework,
                "change_summary": change_summary,
                "timestamp": str(json.dumps({})),
            }

            sns_client.publish(
                TopicArn=self.sns_topic_arn,
                Subject=f"Regulation Update: {framework}",
                Message=json.dumps(message),
            )

            logger.info(f"Notification sent for {framework}")
            return True

        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return False
