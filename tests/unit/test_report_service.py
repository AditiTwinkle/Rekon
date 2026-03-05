"""Unit tests for report service."""

from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from rekon.services.report_service import ReportService, ReportTypeEnum
from rekon.domain.models.regulation import FrameworkEnum


@pytest.fixture
def report_service(db_session: Session) -> ReportService:
    """Create report service instance."""
    return ReportService(db_session)


@pytest.fixture
def test_data():
    """Create test data."""
    return {
        "organization_id": uuid4(),
    }


class TestReportGeneration:
    """Tests for report generation."""

    def test_generate_executive_summary(self, report_service, test_data):
        """Test executive summary generation."""
        report = report_service.generate_executive_summary(test_data["organization_id"])

        assert report["report_type"] == ReportTypeEnum.EXECUTIVE_SUMMARY.value
        assert report["organization_id"] == str(test_data["organization_id"])
        assert "sections" in report
        assert "overview" in report["sections"]
        assert "compliance_scores" in report["sections"]
        assert "key_findings" in report["sections"]
        assert "recommendations" in report["sections"]

    def test_generate_executive_summary_with_framework(self, report_service, test_data):
        """Test executive summary generation with framework filter."""
        report = report_service.generate_executive_summary(
            test_data["organization_id"],
            framework=FrameworkEnum.DORA_A,
        )

        assert report["framework"] == FrameworkEnum.DORA_A.value

    def test_generate_detailed_findings(self, report_service, test_data):
        """Test detailed findings generation."""
        report = report_service.generate_detailed_findings(test_data["organization_id"])

        assert report["report_type"] == ReportTypeEnum.DETAILED_FINDINGS.value
        assert "sections" in report
        assert "compliance_status" in report["sections"]
        assert "identified_gaps" in report["sections"]
        assert "control_assessment" in report["sections"]
        assert "evidence_summary" in report["sections"]

    def test_generate_remediation_status(self, report_service, test_data):
        """Test remediation status generation."""
        report = report_service.generate_remediation_status(test_data["organization_id"])

        assert report["report_type"] == ReportTypeEnum.REMEDIATION_STATUS.value
        assert "sections" in report
        assert "open_gaps" in report["sections"]
        assert "remediation_plans" in report["sections"]
        assert "progress_tracking" in report["sections"]
        assert "timeline" in report["sections"]

    def test_generate_regulatory_format_dora(self, report_service, test_data):
        """Test regulatory format generation for DORA."""
        report = report_service.generate_regulatory_format(
            test_data["organization_id"],
            FrameworkEnum.DORA_A,
        )

        assert report["report_type"] == ReportTypeEnum.REGULATORY_FORMAT.value
        assert report["framework"] == FrameworkEnum.DORA_A.value
        assert "sections" in report

    def test_generate_regulatory_format_sox(self, report_service, test_data):
        """Test regulatory format generation for SOX."""
        report = report_service.generate_regulatory_format(
            test_data["organization_id"],
            FrameworkEnum.SOX,
        )

        assert report["framework"] == FrameworkEnum.SOX.value

    def test_generate_regulatory_format_bmr(self, report_service, test_data):
        """Test regulatory format generation for BMR."""
        report = report_service.generate_regulatory_format(
            test_data["organization_id"],
            FrameworkEnum.BMR,
        )

        assert report["framework"] == FrameworkEnum.BMR.value


class TestReportSections:
    """Tests for report sections."""

    def test_compliance_scores_section(self, report_service, test_data):
        """Test compliance scores section."""
        report = report_service.generate_executive_summary(test_data["organization_id"])
        scores = report["sections"]["compliance_scores"]

        assert "overall_score" in scores
        assert "framework_scores" in scores
        assert "trend" in scores
        assert scores["overall_score"] > 0

    def test_key_findings_section(self, report_service, test_data):
        """Test key findings section."""
        report = report_service.generate_executive_summary(test_data["organization_id"])
        findings = report["sections"]["key_findings"]

        assert "critical_gaps" in findings
        assert "high_priority_gaps" in findings
        assert "top_findings" in findings
        assert len(findings["top_findings"]) > 0

    def test_recommendations_section(self, report_service, test_data):
        """Test recommendations section."""
        report = report_service.generate_executive_summary(test_data["organization_id"])
        recommendations = report["sections"]["recommendations"]

        assert "immediate_actions" in recommendations
        assert "short_term_actions" in recommendations
        assert "long_term_actions" in recommendations

    def test_identified_gaps_section(self, report_service, test_data):
        """Test identified gaps section."""
        report = report_service.generate_detailed_findings(test_data["organization_id"])
        gaps = report["sections"]["identified_gaps"]

        assert "total_gaps" in gaps
        assert "by_severity" in gaps
        assert "by_type" in gaps

    def test_remediation_plans_section(self, report_service, test_data):
        """Test remediation plans section."""
        report = report_service.generate_remediation_status(test_data["organization_id"])
        plans = report["sections"]["remediation_plans"]

        assert "total_plans" in plans
        assert "plans_by_priority" in plans
        assert "estimated_effort_hours" in plans
