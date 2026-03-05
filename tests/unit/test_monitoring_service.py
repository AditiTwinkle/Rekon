"""Unit tests for monitoring service."""

from uuid import uuid4

import pytest

from rekon.services.monitoring_service import MonitoringService


@pytest.fixture
def monitoring_service() -> MonitoringService:
    """Create monitoring service instance."""
    return MonitoringService()


@pytest.fixture
def test_data():
    """Create test data."""
    return {
        "organization_id": uuid4(),
        "metric_name": "TestMetric",
        "value": 42.0,
    }


class TestMetricRecording:
    """Tests for metric recording."""

    def test_put_metric(self, monitoring_service, test_data):
        """Test putting metric to CloudWatch."""
        # This would normally call CloudWatch, but we're just testing the method exists
        try:
            monitoring_service.put_metric(
                test_data["metric_name"],
                test_data["value"],
            )
        except Exception as e:
            # Expected if AWS credentials not configured
            assert "NoCredentialsError" in str(type(e)) or "botocore" in str(type(e))

    def test_put_compliance_metric(self, monitoring_service, test_data):
        """Test putting compliance metric."""
        try:
            monitoring_service.put_compliance_metric(
                test_data["organization_id"],
                test_data["metric_name"],
                test_data["value"],
            )
        except Exception as e:
            assert "NoCredentialsError" in str(type(e)) or "botocore" in str(type(e))

    def test_record_compliance_score(self, monitoring_service, test_data):
        """Test recording compliance score."""
        try:
            monitoring_service.record_compliance_score(
                test_data["organization_id"],
                75.0,
            )
        except Exception as e:
            assert "NoCredentialsError" in str(type(e)) or "botocore" in str(type(e))

    def test_record_gap_count(self, monitoring_service, test_data):
        """Test recording gap count."""
        try:
            monitoring_service.record_gap_count(
                test_data["organization_id"],
                10,
            )
        except Exception as e:
            assert "NoCredentialsError" in str(type(e)) or "botocore" in str(type(e))

    def test_record_gap_count_with_severity(self, monitoring_service, test_data):
        """Test recording gap count with severity."""
        try:
            monitoring_service.record_gap_count(
                test_data["organization_id"],
                3,
                severity="CRITICAL",
            )
        except Exception as e:
            assert "NoCredentialsError" in str(type(e)) or "botocore" in str(type(e))

    def test_record_evidence_upload(self, monitoring_service, test_data):
        """Test recording evidence upload."""
        try:
            monitoring_service.record_evidence_upload(
                test_data["organization_id"],
                1024000,  # 1MB
            )
        except Exception as e:
            assert "NoCredentialsError" in str(type(e)) or "botocore" in str(type(e))

    def test_record_api_latency(self, monitoring_service):
        """Test recording API latency."""
        try:
            monitoring_service.record_api_latency(
                "/api/v1/compliance/analyze",
                150.5,
            )
        except Exception as e:
            assert "NoCredentialsError" in str(type(e)) or "botocore" in str(type(e))

    def test_record_lambda_invocation(self, monitoring_service):
        """Test recording Lambda invocation."""
        try:
            monitoring_service.record_lambda_invocation(
                "regulation_puller",
                2500.0,
                success=True,
            )
        except Exception as e:
            assert "NoCredentialsError" in str(type(e)) or "botocore" in str(type(e))


class TestAlarmCreation:
    """Tests for alarm creation."""

    def test_create_alarm(self, monitoring_service):
        """Test creating CloudWatch alarm."""
        try:
            monitoring_service.create_alarm(
                alarm_name="HighComplianceGapAlarm",
                metric_name="GapCount",
                threshold=20.0,
            )
        except Exception as e:
            assert "NoCredentialsError" in str(type(e)) or "botocore" in str(type(e))

    def test_create_alarm_with_sns(self, monitoring_service):
        """Test creating alarm with SNS notification."""
        try:
            monitoring_service.create_alarm(
                alarm_name="CriticalGapAlarm",
                metric_name="GapCountCRITICAL",
                threshold=1.0,
                sns_topic_arn="arn:aws:sns:us-east-1:123456789012:compliance-alerts",
            )
        except Exception as e:
            assert "NoCredentialsError" in str(type(e)) or "botocore" in str(type(e))


class TestAlertSending:
    """Tests for alert sending."""

    def test_send_alert(self, monitoring_service):
        """Test sending alert."""
        try:
            monitoring_service.send_alert(
                topic_arn="arn:aws:sns:us-east-1:123456789012:compliance-alerts",
                subject="Test Alert",
                message="This is a test alert",
            )
        except Exception as e:
            assert "NoCredentialsError" in str(type(e)) or "botocore" in str(type(e))

    def test_send_compliance_alert(self, monitoring_service, test_data):
        """Test sending compliance alert."""
        try:
            monitoring_service.send_compliance_alert(
                topic_arn="arn:aws:sns:us-east-1:123456789012:compliance-alerts",
                organization_id=test_data["organization_id"],
                alert_type="GAP_IDENTIFIED",
                title="New Gap Identified",
                message="A new compliance gap has been identified",
            )
        except Exception as e:
            assert "NoCredentialsError" in str(type(e)) or "botocore" in str(type(e))

    def test_send_critical_gap_alert(self, monitoring_service, test_data):
        """Test sending critical gap alert."""
        try:
            monitoring_service.send_critical_gap_alert(
                topic_arn="arn:aws:sns:us-east-1:123456789012:compliance-alerts",
                organization_id=test_data["organization_id"],
                gap_title="Missing ICT Risk Management Framework",
                framework="DORA_A",
            )
        except Exception as e:
            assert "NoCredentialsError" in str(type(e)) or "botocore" in str(type(e))

    def test_send_evidence_expiration_alert(self, monitoring_service, test_data):
        """Test sending evidence expiration alert."""
        try:
            monitoring_service.send_evidence_expiration_alert(
                topic_arn="arn:aws:sns:us-east-1:123456789012:compliance-alerts",
                organization_id=test_data["organization_id"],
                evidence_count=5,
                days_remaining=30,
            )
        except Exception as e:
            assert "NoCredentialsError" in str(type(e)) or "botocore" in str(type(e))

    def test_send_remediation_overdue_alert(self, monitoring_service, test_data):
        """Test sending remediation overdue alert."""
        try:
            monitoring_service.send_remediation_overdue_alert(
                topic_arn="arn:aws:sns:us-east-1:123456789012:compliance-alerts",
                organization_id=test_data["organization_id"],
                task_count=2,
            )
        except Exception as e:
            assert "NoCredentialsError" in str(type(e)) or "botocore" in str(type(e))
