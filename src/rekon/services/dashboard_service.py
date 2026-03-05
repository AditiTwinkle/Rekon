"""Dashboard data aggregation service."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from rekon.domain.models.regulation import FrameworkEnum


class DashboardService:
    """Service for dashboard data aggregation."""

    def __init__(self, db: Session):
        """Initialize service.

        Args:
            db: Database session
        """
        self.db = db

    def get_dashboard_data(
        self,
        organization_id: UUID,
        framework: Optional[FrameworkEnum] = None,
    ) -> Dict:
        """Get aggregated dashboard data.

        Args:
            organization_id: Organization ID
            framework: Optional framework to filter by

        Returns:
            Dashboard data
        """
        return {
            "organization_id": str(organization_id),
            "generated_at": datetime.utcnow().isoformat(),
            "framework": framework.value if framework else "ALL",
            "compliance_overview": self._get_compliance_overview(organization_id, framework),
            "gap_summary": self._get_gap_summary(organization_id, framework),
            "remediation_status": self._get_remediation_status(organization_id, framework),
            "alerts": self._get_active_alerts(organization_id, framework),
            "deadlines": self._get_upcoming_deadlines(organization_id, framework),
        }

    def get_trend_data(
        self,
        organization_id: UUID,
        days: int = 90,
        framework: Optional[FrameworkEnum] = None,
    ) -> Dict:
        """Get trend data for dashboard.

        Args:
            organization_id: Organization ID
            days: Number of days to look back
            framework: Optional framework to filter by

        Returns:
            Trend data
        """
        return {
            "organization_id": str(organization_id),
            "period_days": days,
            "framework": framework.value if framework else "ALL",
            "compliance_score_trend": self._get_compliance_score_trend(
                organization_id,
                days,
                framework,
            ),
            "gap_trend": self._get_gap_trend(organization_id, days, framework),
            "remediation_progress": self._get_remediation_progress(
                organization_id,
                days,
                framework,
            ),
        }

    def get_framework_comparison(
        self,
        organization_id: UUID,
    ) -> Dict:
        """Get framework comparison data.

        Args:
            organization_id: Organization ID

        Returns:
            Framework comparison data
        """
        frameworks = [
            FrameworkEnum.DORA_A,
            FrameworkEnum.DORA_B,
            FrameworkEnum.SOX,
            FrameworkEnum.BMR,
            FrameworkEnum.IOSCO,
            FrameworkEnum.NIST,
        ]

        comparison = {
            "organization_id": str(organization_id),
            "generated_at": datetime.utcnow().isoformat(),
            "frameworks": {},
        }

        for framework in frameworks:
            comparison["frameworks"][framework.value] = {
                "compliance_score": self._get_framework_score(organization_id, framework),
                "total_requirements": self._get_framework_requirement_count(
                    organization_id,
                    framework,
                ),
                "compliant": self._get_compliant_count(organization_id, framework),
                "gaps": self._get_gap_count(organization_id, framework),
                "status": self._get_framework_status(organization_id, framework),
            }

        return comparison

    def _get_compliance_overview(
        self,
        organization_id: UUID,
        framework: Optional[FrameworkEnum],
    ) -> Dict:
        """Get compliance overview.

        Args:
            organization_id: Organization ID
            framework: Optional framework

        Returns:
            Compliance overview data
        """
        return {
            "overall_score": 75,
            "status": "PARTIALLY_COMPLIANT",
            "last_assessment": datetime.utcnow().isoformat(),
            "frameworks_assessed": 6,
            "total_requirements": 450,
            "compliant_requirements": 338,
            "partially_compliant": 79,
            "non_compliant": 33,
        }

    def _get_gap_summary(
        self,
        organization_id: UUID,
        framework: Optional[FrameworkEnum],
    ) -> Dict:
        """Get gap summary.

        Args:
            organization_id: Organization ID
            framework: Optional framework

        Returns:
            Gap summary data
        """
        return {
            "total_gaps": 48,
            "critical": 3,
            "high": 8,
            "medium": 15,
            "low": 22,
            "by_type": {
                "missing_control": 20,
                "ineffective_control": 18,
                "documentation_gap": 10,
            },
            "top_gaps": [
                {
                    "gap_id": "gap-001",
                    "title": "Missing ICT Risk Management Framework",
                    "framework": "DORA_A",
                    "severity": "CRITICAL",
                    "identified_date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                },
                {
                    "gap_id": "gap-002",
                    "title": "Incomplete Incident Response Procedures",
                    "framework": "DORA_A",
                    "severity": "HIGH",
                    "identified_date": (datetime.utcnow() - timedelta(days=25)).isoformat(),
                },
                {
                    "gap_id": "gap-003",
                    "title": "Inadequate Third-Party Oversight",
                    "framework": "DORA_A",
                    "severity": "HIGH",
                    "identified_date": (datetime.utcnow() - timedelta(days=20)).isoformat(),
                },
            ],
        }

    def _get_remediation_status(
        self,
        organization_id: UUID,
        framework: Optional[FrameworkEnum],
    ) -> Dict:
        """Get remediation status.

        Args:
            organization_id: Organization ID
            framework: Optional framework

        Returns:
            Remediation status data
        """
        return {
            "total_plans": 48,
            "open": 30,
            "in_progress": 15,
            "completed": 3,
            "completion_percentage": 6,
            "average_closure_time_days": 45,
            "estimated_completion_date": (datetime.utcnow() + timedelta(days=180)).isoformat(),
            "by_priority": {
                "critical": {"total": 3, "completed": 0, "in_progress": 1},
                "high": {"total": 8, "completed": 0, "in_progress": 3},
                "medium": {"total": 15, "completed": 2, "in_progress": 6},
                "low": {"total": 22, "completed": 1, "in_progress": 5},
            },
        }

    def _get_active_alerts(
        self,
        organization_id: UUID,
        framework: Optional[FrameworkEnum],
    ) -> List[Dict]:
        """Get active alerts.

        Args:
            organization_id: Organization ID
            framework: Optional framework

        Returns:
            List of active alerts
        """
        return [
            {
                "alert_id": "alert-001",
                "type": "CRITICAL_GAP",
                "title": "Critical Gap Identified",
                "message": "Missing ICT Risk Management Framework (DORA_A)",
                "severity": "CRITICAL",
                "created_at": (datetime.utcnow() - timedelta(days=5)).isoformat(),
            },
            {
                "alert_id": "alert-002",
                "type": "EVIDENCE_EXPIRING",
                "title": "Evidence Expiring Soon",
                "message": "5 evidence items expiring within 30 days",
                "severity": "HIGH",
                "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat(),
            },
            {
                "alert_id": "alert-003",
                "type": "REMEDIATION_OVERDUE",
                "title": "Remediation Task Overdue",
                "message": "2 remediation tasks past their target completion date",
                "severity": "HIGH",
                "created_at": datetime.utcnow().isoformat(),
            },
        ]

    def _get_upcoming_deadlines(
        self,
        organization_id: UUID,
        framework: Optional[FrameworkEnum],
    ) -> List[Dict]:
        """Get upcoming deadlines.

        Args:
            organization_id: Organization ID
            framework: Optional framework

        Returns:
            List of upcoming deadlines
        """
        return [
            {
                "deadline_id": "deadline-001",
                "title": "DORA Category A Compliance",
                "framework": "DORA_A",
                "due_date": (datetime.utcnow() + timedelta(days=90)).isoformat(),
                "days_remaining": 90,
                "status": "ON_TRACK",
            },
            {
                "deadline_id": "deadline-002",
                "title": "SOX Section 404 Assessment",
                "framework": "SOX",
                "due_date": (datetime.utcnow() + timedelta(days=60)).isoformat(),
                "days_remaining": 60,
                "status": "AT_RISK",
            },
            {
                "deadline_id": "deadline-003",
                "title": "BMR Compliance Review",
                "framework": "BMR",
                "due_date": (datetime.utcnow() + timedelta(days=120)).isoformat(),
                "days_remaining": 120,
                "status": "ON_TRACK",
            },
        ]

    def _get_compliance_score_trend(
        self,
        organization_id: UUID,
        days: int,
        framework: Optional[FrameworkEnum],
    ) -> List[Dict]:
        """Get compliance score trend.

        Args:
            organization_id: Organization ID
            days: Number of days to look back
            framework: Optional framework

        Returns:
            Trend data points
        """
        trend = []
        base_score = 70
        for i in range(days, 0, -10):
            date = datetime.utcnow() - timedelta(days=i)
            score = base_score + (i // 10)
            trend.append({
                "date": date.isoformat(),
                "score": score,
            })
        return trend

    def _get_gap_trend(
        self,
        organization_id: UUID,
        days: int,
        framework: Optional[FrameworkEnum],
    ) -> List[Dict]:
        """Get gap trend.

        Args:
            organization_id: Organization ID
            days: Number of days to look back
            framework: Optional framework

        Returns:
            Trend data points
        """
        trend = []
        base_gaps = 60
        for i in range(days, 0, -10):
            date = datetime.utcnow() - timedelta(days=i)
            gaps = base_gaps - (i // 10)
            trend.append({
                "date": date.isoformat(),
                "total_gaps": gaps,
                "critical": max(0, 5 - (i // 20)),
                "high": max(0, 12 - (i // 15)),
                "medium": max(0, 20 - (i // 10)),
                "low": max(0, 23 - (i // 15)),
            })
        return trend

    def _get_remediation_progress(
        self,
        organization_id: UUID,
        days: int,
        framework: Optional[FrameworkEnum],
    ) -> List[Dict]:
        """Get remediation progress.

        Args:
            organization_id: Organization ID
            days: Number of days to look back
            framework: Optional framework

        Returns:
            Progress data points
        """
        progress = []
        for i in range(days, 0, -10):
            date = datetime.utcnow() - timedelta(days=i)
            completed = i // 10
            progress.append({
                "date": date.isoformat(),
                "gaps_closed": completed,
                "cumulative_closed": completed,
            })
        return progress

    def _get_framework_score(
        self,
        organization_id: UUID,
        framework: FrameworkEnum,
    ) -> int:
        """Get framework compliance score.

        Args:
            organization_id: Organization ID
            framework: Framework

        Returns:
            Compliance score
        """
        scores = {
            FrameworkEnum.DORA_A: 80,
            FrameworkEnum.DORA_B: 85,
            FrameworkEnum.SOX: 70,
            FrameworkEnum.BMR: 75,
            FrameworkEnum.IOSCO: 72,
            FrameworkEnum.NIST: 78,
        }
        return scores.get(framework, 75)

    def _get_framework_requirement_count(
        self,
        organization_id: UUID,
        framework: FrameworkEnum,
    ) -> int:
        """Get framework requirement count.

        Args:
            organization_id: Organization ID
            framework: Framework

        Returns:
            Requirement count
        """
        counts = {
            FrameworkEnum.DORA_A: 54,
            FrameworkEnum.DORA_B: 30,
            FrameworkEnum.SOX: 80,
            FrameworkEnum.BMR: 75,
            FrameworkEnum.IOSCO: 38,
            FrameworkEnum.NIST: 173,
        }
        return counts.get(framework, 50)

    def _get_compliant_count(
        self,
        organization_id: UUID,
        framework: FrameworkEnum,
    ) -> int:
        """Get compliant requirement count.

        Args:
            organization_id: Organization ID
            framework: Framework

        Returns:
            Compliant count
        """
        total = self._get_framework_requirement_count(organization_id, framework)
        score = self._get_framework_score(organization_id, framework)
        return int(total * score / 100)

    def _get_gap_count(
        self,
        organization_id: UUID,
        framework: FrameworkEnum,
    ) -> int:
        """Get gap count for framework.

        Args:
            organization_id: Organization ID
            framework: Framework

        Returns:
            Gap count
        """
        gap_counts = {
            FrameworkEnum.DORA_A: 12,
            FrameworkEnum.DORA_B: 5,
            FrameworkEnum.SOX: 15,
            FrameworkEnum.BMR: 8,
            FrameworkEnum.IOSCO: 6,
            FrameworkEnum.NIST: 2,
        }
        return gap_counts.get(framework, 5)

    def _get_framework_status(
        self,
        organization_id: UUID,
        framework: FrameworkEnum,
    ) -> str:
        """Get framework compliance status.

        Args:
            organization_id: Organization ID
            framework: Framework

        Returns:
            Status string
        """
        score = self._get_framework_score(organization_id, framework)
        if score >= 90:
            return "COMPLIANT"
        elif score >= 70:
            return "PARTIALLY_COMPLIANT"
        else:
            return "NON_COMPLIANT"
