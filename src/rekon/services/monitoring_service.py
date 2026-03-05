"""Monitoring and alerting service."""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID

import boto3

logger = logging.getLogger(__name__)

# Initialize AWS clients
cloudwatch = boto3.client("cloudwatch")
sns = boto3.client("sns")


class MonitoringService:
    """Service for monitoring and alerting."""

    def __init__(self, namespace: str = "Rekon"):
        """Initialize service.

        Args:
            namespace: CloudWatch namespace
        """
        self.namespace = namespace

    def put_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "Count",
        dimensions: Optional[Dict[str, str]] = None,
    ) -> None:
        """Put metric to CloudWatch.

        Args:
            metric_name: Metric name
            value: Metric value
            unit: Metric unit
            dimensions: Optional dimensions
        """
        try:
            metric_data = {
                "MetricName": metric_name,
                "Value": value,
                "Unit": unit,
                "Timestamp": datetime.utcnow(),
            }

            if dimensions:
                metric_data["Dimensions"] = [
                    {"Name": k, "Value": v} for k, v in dimensions.items()
                ]

            cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[metric_data],
            )

            logger.debug(f"Metric {metric_name} recorded: {value}")

        except Exception as e:
            logger.error(f"Error putting metric: {str(e)}")

    def put_compliance_metric(
        self,
        organization_id: UUID,
        metric_name: str,
        value: float,
        framework: Optional[str] = None,
    ) -> None:
        """Put compliance metric to CloudWatch.

        Args:
            organization_id: Organization ID
            metric_name: Metric name
            value: Metric value
            framework: Optional framework
        """
        dimensions = {
            "OrganizationId": str(organization_id),
        }

        if framework:
            dimensions["Framework"] = framework

        self.put_metric(metric_name, value, dimensions=dimensions)

    def record_compliance_score(
        self,
        organization_id: UUID,
        score: float,
        framework: Optional[str] = None,
    ) -> None:
        """Record compliance score metric.

        Args:
            organization_id: Organization ID
            score: Compliance score (0-100)
            framework: Optional framework
        """
        self.put_compliance_metric(
            organization_id,
            "ComplianceScore",
            score,
            framework,
        )

    def record_gap_count(
        self,
        organization_id: UUID,
        count: int,
        severity: Optional[str] = None,
        framework: Optional[str] = None,
    ) -> None:
        """Record gap count metric.

        Args:
            organization_id: Organization ID
            count: Number of gaps
            severity: Optional severity level
            framework: Optional framework
        """
        metric_name = f"GapCount{severity}" if severity else "GapCount"
        self.put_compliance_metric(
            organization_id,
            metric_name,
            count,
            framework,
        )

    def record_evidence_upload(
        self,
        organization_id: UUID,
        file_size: int,
    ) -> None:
        """Record evidence upload metric.

        Args:
            organization_id: Organization ID
            file_size: File size in bytes
        """
        self.put_compliance_metric(
            organization_id,
            "EvidenceUploadSize",
            file_size,
        )

    def record_api_latency(
        self,
        endpoint: str,
        latency_ms: float,
    ) -> None:
        """Record API latency metric.

        Args:
            endpoint: API endpoint
            latency_ms: Latency in milliseconds
        """
        self.put_metric(
            "APILatency",
            latency_ms,
            unit="Milliseconds",
            dimensions={"Endpoint": endpoint},
        )

    def record_lambda_invocation(
        self,
        function_name: str,
        duration_ms: float,
        success: bool,
    ) -> None:
        """Record Lambda invocation metric.

        Args:
            function_name: Lambda function name
            duration_ms: Duration in milliseconds
            success: Whether invocation was successful
        """
        self.put_metric(
            "LambdaInvocation",
            1,
            dimensions={
                "FunctionName": function_name,
                "Status": "Success" if success else "Failure",
            },
        )

        self.put_metric(
            "LambdaDuration",
            duration_ms,
            unit="Milliseconds",
            dimensions={"FunctionName": function_name},
        )

    def create_alarm(
        self,
        alarm_name: str,
        metric_name: str,
        threshold: float,
        comparison_operator: str = "GreaterThanThreshold",
        evaluation_periods: int = 1,
        period: int = 300,
        statistic: str = "Average",
        alarm_description: str = "",
        sns_topic_arn: Optional[str] = None,
    ) -> None:
        """Create CloudWatch alarm.

        Args:
            alarm_name: Alarm name
            metric_name: Metric name
            threshold: Alarm threshold
            comparison_operator: Comparison operator
            evaluation_periods: Number of evaluation periods
            period: Period in seconds
            statistic: Statistic (Average, Sum, Maximum, Minimum)
            alarm_description: Alarm description
            sns_topic_arn: Optional SNS topic for notifications
        """
        try:
            alarm_params = {
                "AlarmName": alarm_name,
                "MetricName": metric_name,
                "Namespace": self.namespace,
                "Statistic": statistic,
                "Period": period,
                "EvaluationPeriods": evaluation_periods,
                "Threshold": threshold,
                "ComparisonOperator": comparison_operator,
                "AlarmDescription": alarm_description,
            }

            if sns_topic_arn:
                alarm_params["AlarmActions"] = [sns_topic_arn]

            cloudwatch.put_metric_alarm(**alarm_params)

            logger.info(f"Alarm {alarm_name} created")

        except Exception as e:
            logger.error(f"Error creating alarm: {str(e)}")

    def send_alert(
        self,
        topic_arn: str,
        subject: str,
        message: str,
        alert_type: str = "INFO",
    ) -> None:
        """Send alert via SNS.

        Args:
            topic_arn: SNS topic ARN
            subject: Alert subject
            message: Alert message
            alert_type: Alert type (INFO, WARNING, CRITICAL)
        """
        try:
            alert_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "type": alert_type,
                "subject": subject,
                "message": message,
            }

            sns.publish(
                TopicArn=topic_arn,
                Subject=f"[{alert_type}] {subject}",
                Message=json.dumps(alert_data, indent=2),
            )

            logger.info(f"Alert sent: {subject}")

        except Exception as e:
            logger.error(f"Error sending alert: {str(e)}")

    def send_compliance_alert(
        self,
        topic_arn: str,
        organization_id: UUID,
        alert_type: str,
        title: str,
        message: str,
        severity: str = "HIGH",
    ) -> None:
        """Send compliance alert.

        Args:
            topic_arn: SNS topic ARN
            organization_id: Organization ID
            alert_type: Alert type
            title: Alert title
            message: Alert message
            severity: Alert severity
        """
        alert_message = f"""
Organization: {organization_id}
Alert Type: {alert_type}
Severity: {severity}

{message}
"""

        self.send_alert(
            topic_arn,
            title,
            alert_message,
            alert_type=severity,
        )

    def send_critical_gap_alert(
        self,
        topic_arn: str,
        organization_id: UUID,
        gap_title: str,
        framework: str,
    ) -> None:
        """Send critical gap alert.

        Args:
            topic_arn: SNS topic ARN
            organization_id: Organization ID
            gap_title: Gap title
            framework: Framework name
        """
        message = f"""
A critical compliance gap has been identified:

Gap: {gap_title}
Framework: {framework}

Please review and take immediate action.
"""

        self.send_compliance_alert(
            topic_arn,
            organization_id,
            "CRITICAL_GAP",
            f"Critical Gap: {gap_title}",
            message,
            severity="CRITICAL",
        )

    def send_evidence_expiration_alert(
        self,
        topic_arn: str,
        organization_id: UUID,
        evidence_count: int,
        days_remaining: int,
    ) -> None:
        """Send evidence expiration alert.

        Args:
            topic_arn: SNS topic ARN
            organization_id: Organization ID
            evidence_count: Number of expiring evidence items
            days_remaining: Days until expiration
        """
        message = f"""
{evidence_count} evidence items are expiring in {days_remaining} days.

Please review and update evidence as needed.
"""

        self.send_compliance_alert(
            topic_arn,
            organization_id,
            "EVIDENCE_EXPIRING",
            f"Evidence Expiring Soon ({evidence_count} items)",
            message,
            severity="HIGH",
        )

    def send_remediation_overdue_alert(
        self,
        topic_arn: str,
        organization_id: UUID,
        task_count: int,
    ) -> None:
        """Send remediation overdue alert.

        Args:
            topic_arn: SNS topic ARN
            organization_id: Organization ID
            task_count: Number of overdue tasks
        """
        message = f"""
{task_count} remediation tasks are overdue.

Please review and update task status.
"""

        self.send_compliance_alert(
            topic_arn,
            organization_id,
            "REMEDIATION_OVERDUE",
            f"Remediation Tasks Overdue ({task_count} tasks)",
            message,
            severity="HIGH",
        )
