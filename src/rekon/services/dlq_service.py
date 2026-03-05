"""Dead-letter queue service for failed operations."""

import logging
import json
from typing import Dict, Optional

import boto3

logger = logging.getLogger(__name__)

sqs_client = boto3.client("sqs")


class DLQService:
    """Service for managing dead-letter queues."""

    def __init__(self, dlq_url: str = None):
        """Initialize DLQ service.

        Args:
            dlq_url: SQS queue URL for dead-letter queue
        """
        self.dlq_url = dlq_url

    def send_to_dlq(
        self,
        message_body: Dict,
        message_group_id: Optional[str] = None,
    ) -> bool:
        """Send message to dead-letter queue.

        Args:
            message_body: Message body dictionary
            message_group_id: Message group ID for FIFO queues

        Returns:
            True if successful, False otherwise
        """
        if not self.dlq_url:
            logger.warning("DLQ URL not configured")
            return False

        try:
            kwargs = {
                "QueueUrl": self.dlq_url,
                "MessageBody": json.dumps(message_body),
            }

            if message_group_id:
                kwargs["MessageGroupId"] = message_group_id

            response = sqs_client.send_message(**kwargs)

            logger.info(f"Message sent to DLQ: {response.get('MessageId')}")
            return True

        except Exception as e:
            logger.error(f"Error sending to DLQ: {str(e)}")
            return False

    def get_dlq_messages(self, max_messages: int = 10) -> list:
        """Retrieve messages from dead-letter queue.

        Args:
            max_messages: Maximum number of messages to retrieve

        Returns:
            List of messages
        """
        if not self.dlq_url:
            logger.warning("DLQ URL not configured")
            return []

        try:
            response = sqs_client.receive_message(
                QueueUrl=self.dlq_url,
                MaxNumberOfMessages=max_messages,
            )

            messages = response.get("Messages", [])
            logger.info(f"Retrieved {len(messages)} messages from DLQ")
            return messages

        except Exception as e:
            logger.error(f"Error retrieving from DLQ: {str(e)}")
            return []

    def delete_dlq_message(self, receipt_handle: str) -> bool:
        """Delete message from dead-letter queue.

        Args:
            receipt_handle: Message receipt handle

        Returns:
            True if successful, False otherwise
        """
        if not self.dlq_url:
            logger.warning("DLQ URL not configured")
            return False

        try:
            sqs_client.delete_message(
                QueueUrl=self.dlq_url,
                ReceiptHandle=receipt_handle,
            )

            logger.info("Message deleted from DLQ")
            return True

        except Exception as e:
            logger.error(f"Error deleting from DLQ: {str(e)}")
            return False
