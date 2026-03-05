"""Unit tests for dashboard service."""

from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from rekon.services.dashboard_service import DashboardService
from rekon.domain.models.regulation import FrameworkEnum


@pytest.fixture
def dashboard_service(db_session: Session) -> DashboardService:
    """Create dashboard service instance."""
    return DashboardService(db_session)


@pytest.fixture
def test_data():
    """Create test data."""
    return {
        "organization_id": uuid4(),
    }


class TestDashboardData:
    """Tests for dashboard data retrieval."""

    def test_get_dashboard_data(self, dashboard_service, test_data):
        """Test getting dashboard data."""
        data = dashboard_service.get_dashboard_data(test_data["organization_id"])

        assert data["organization_id"] == str(test_data["organization_id"])
        assert "generated_at" in data
        assert "compliance_overview" in data
        assert "gap_summary" in data
        assert "remediation_status" in data
        assert "alerts" in data
        assert "deadlines" in data

    def test_get_dashboard_data_with_framework(self, dashboard_service, test_data):
        """Test getting dashboard data with framework filter."""
        data = dashboard_service.get_dashboard_data(
            test_data["organization_id"],
            framework=FrameworkEnum.DORA_A,
        )

        assert data["framework"] == FrameworkEnum.DORA_A.value

    def test_compliance_overview_section(self, dashboard_service, test_data):
        """Test compliance overview section."""
        data = dashboard_service.get_dashboard_data(test_data["organization_id"])
        overview = data["compliance_overview"]

        assert "overall_score" in overview
        assert "status" in overview
        assert "last_assessment" in overview
        assert "frameworks_assessed" in overview
        assert "total_requirements" in overview

    def test_gap_summary_section(self, dashboard_service, test_data):
        """Test gap summary section."""
        data = dashboard_service.get_dashboard_data(test_data["organization_id"])
        gaps = data["gap_summary"]

        assert "total_gaps" in gaps
        assert "critical" in gaps
        assert "high" in gaps
        assert "medium" in gaps
        assert "low" in gaps
        assert "top_gaps" in gaps
        assert len(gaps["top_gaps"]) > 0

    def test_remediation_status_section(self, dashboard_service, test_data):
        """Test remediation status section."""
        data = dashboard_service.get_dashboard_data(test_data["organization_id"])
        remediation = data["remediation_status"]

        assert "total_plans" in remediation
        assert "open" in remediation
        assert "in_progress" in remediation
        assert "completed" in remediation
        assert "by_priority" in remediation

    def test_alerts_section(self, dashboard_service, test_data):
        """Test alerts section."""
        data = dashboard_service.get_dashboard_data(test_data["organization_id"])
        alerts = data["alerts"]

        assert isinstance(alerts, list)
        assert len(alerts) > 0
        for alert in alerts:
            assert "alert_id" in alert
            assert "type" in alert
            assert "severity" in alert

    def test_deadlines_section(self, dashboard_service, test_data):
        """Test deadlines section."""
        data = dashboard_service.get_dashboard_data(test_data["organization_id"])
        deadlines = data["deadlines"]

        assert isinstance(deadlines, list)
        assert len(deadlines) > 0
        for deadline in deadlines:
            assert "deadline_id" in deadline
            assert "title" in deadline
            assert "due_date" in deadline
            assert "days_remaining" in deadline


class TestTrendData:
    """Tests for trend data."""

    def test_get_trend_data(self, dashboard_service, test_data):
        """Test getting trend data."""
        trend = dashboard_service.get_trend_data(test_data["organization_id"])

        assert trend["organization_id"] == str(test_data["organization_id"])
        assert "period_days" in trend
        assert "compliance_score_trend" in trend
        assert "gap_trend" in trend
        assert "remediation_progress" in trend

    def test_compliance_score_trend(self, dashboard_service, test_data):
        """Test compliance score trend."""
        trend = dashboard_service.get_trend_data(test_data["organization_id"], days=90)
        score_trend = trend["compliance_score_trend"]

        assert isinstance(score_trend, list)
        assert len(score_trend) > 0
        for point in score_trend:
            assert "date" in point
            assert "score" in point

    def test_gap_trend(self, dashboard_service, test_data):
        """Test gap trend."""
        trend = dashboard_service.get_trend_data(test_data["organization_id"], days=90)
        gap_trend = trend["gap_trend"]

        assert isinstance(gap_trend, list)
        assert len(gap_trend) > 0
        for point in gap_trend:
            assert "date" in point
            assert "total_gaps" in point
            assert "critical" in point
            assert "high" in point

    def test_remediation_progress_trend(self, dashboard_service, test_data):
        """Test remediation progress trend."""
        trend = dashboard_service.get_trend_data(test_data["organization_id"], days=90)
        progress = trend["remediation_progress"]

        assert isinstance(progress, list)
        assert len(progress) > 0
        for point in progress:
            assert "date" in point
            assert "gaps_closed" in point


class TestFrameworkComparison:
    """Tests for framework comparison."""

    def test_get_framework_comparison(self, dashboard_service, test_data):
        """Test getting framework comparison."""
        comparison = dashboard_service.get_framework_comparison(test_data["organization_id"])

        assert comparison["organization_id"] == str(test_data["organization_id"])
        assert "frameworks" in comparison
        assert len(comparison["frameworks"]) > 0

    def test_framework_comparison_data(self, dashboard_service, test_data):
        """Test framework comparison data structure."""
        comparison = dashboard_service.get_framework_comparison(test_data["organization_id"])
        frameworks = comparison["frameworks"]

        for framework_name, framework_data in frameworks.items():
            assert "compliance_score" in framework_data
            assert "total_requirements" in framework_data
            assert "compliant" in framework_data
            assert "gaps" in framework_data
            assert "status" in framework_data

    def test_framework_comparison_scores(self, dashboard_service, test_data):
        """Test framework comparison scores."""
        comparison = dashboard_service.get_framework_comparison(test_data["organization_id"])
        frameworks = comparison["frameworks"]

        # Check that scores are reasonable
        for framework_name, framework_data in frameworks.items():
            score = framework_data["compliance_score"]
            assert 0 <= score <= 100

    def test_framework_comparison_status(self, dashboard_service, test_data):
        """Test framework comparison status."""
        comparison = dashboard_service.get_framework_comparison(test_data["organization_id"])
        frameworks = comparison["frameworks"]

        valid_statuses = ["COMPLIANT", "PARTIALLY_COMPLIANT", "NON_COMPLIANT"]
        for framework_name, framework_data in frameworks.items():
            assert framework_data["status"] in valid_statuses
