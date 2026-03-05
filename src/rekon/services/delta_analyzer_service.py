"""Delta analyzer service for compliance gap analysis."""

import logging
from typing import List, Dict, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from rekon.db.repositories.gap import GapRepository
from rekon.db.repositories.compliance_state import ComplianceStateRepository
from rekon.db.repositories.regulation import RegulationRepository
from rekon.domain.models.gap import (
    ComplianceGapCreate,
    GapTypeEnum,
    GapSeverityEnum,
    GapStatusEnum,
)
from rekon.domain.models.compliance_state import (
    ComplianceStatusEnum,
    ComplianceScoreResponse,
)
from rekon.domain.models.regulation import FrameworkEnum

logger = logging.getLogger(__name__)


class DeltaAnalyzerService:
    """Service for delta analysis and gap identification."""

    def __init__(self, db: Session):
        """Initialize service.

        Args:
            db: Database session
        """
        self.db = db
        self.gap_repository = GapRepository(db)
        self.compliance_repository = ComplianceStateRepository(db)
        self.regulation_repository = RegulationRepository(db)

    def analyze_compliance_delta(
        self,
        organization_id: UUID,
        user_id: UUID,
    ) -> Dict:
        """Analyze compliance delta for an organization.

        Args:
            organization_id: Organization ID
            user_id: User ID performing analysis

        Returns:
            Analysis results with identified gaps
        """
        logger.info(f"Starting delta analysis for organization {organization_id}")

        # Get all compliance states for organization
        compliance_states = self.compliance_repository.list_by_organization(
            organization_id, skip=0, limit=10000
        )

        # Identify gaps based on compliance states
        gaps_identified = []

        for state in compliance_states:
            if state.status == ComplianceStatusEnum.NON_COMPLIANT:
                gap = self._create_gap_for_state(
                    organization_id,
                    state,
                    GapTypeEnum.MISSING_CONTROL,
                    user_id,
                )
                gaps_identified.append(gap)
            elif state.status == ComplianceStatusEnum.PARTIALLY_COMPLIANT:
                gap = self._create_gap_for_state(
                    organization_id,
                    state,
                    GapTypeEnum.INEFFECTIVE_CONTROL,
                    user_id,
                )
                gaps_identified.append(gap)

        # Calculate compliance scores
        scores = self._calculate_compliance_scores(organization_id)

        logger.info(
            f"Delta analysis complete for organization {organization_id}: "
            f"{len(gaps_identified)} gaps identified"
        )

        return {
            "organization_id": organization_id,
            "gaps_identified": gaps_identified,
            "compliance_scores": scores,
            "analysis_timestamp": None,  # Will be set by caller
        }

    def _create_gap_for_state(
        self,
        organization_id: UUID,
        state,
        gap_type: GapTypeEnum,
        user_id: UUID,
    ):
        """Create a gap record for a compliance state.

        Args:
            organization_id: Organization ID
            state: Compliance state
            gap_type: Type of gap
            user_id: User ID

        Returns:
            Created gap
        """
        severity = self._classify_gap_severity(state.status, gap_type)

        gap_create = ComplianceGapCreate(
            organization_id=organization_id,
            checklist_item_id=state.checklist_item_id,
            gap_type=gap_type,
            severity=severity,
            description=f"Gap identified during delta analysis: {gap_type.value}",
            root_cause=None,
            identified_by=user_id,
        )

        gap = self.gap_repository.create(gap_create)
        return gap

    def _classify_gap_severity(
        self,
        status: ComplianceStatusEnum,
        gap_type: GapTypeEnum,
    ) -> GapSeverityEnum:
        """Classify gap severity based on status and type.

        Args:
            status: Compliance status
            gap_type: Gap type

        Returns:
            Gap severity
        """
        if status == ComplianceStatusEnum.NON_COMPLIANT:
            if gap_type == GapTypeEnum.MISSING_CONTROL:
                return GapSeverityEnum.CRITICAL
            elif gap_type == GapTypeEnum.INEFFECTIVE_CONTROL:
                return GapSeverityEnum.HIGH
            else:
                return GapSeverityEnum.MEDIUM
        elif status == ComplianceStatusEnum.PARTIALLY_COMPLIANT:
            if gap_type == GapTypeEnum.INEFFECTIVE_CONTROL:
                return GapSeverityEnum.HIGH
            else:
                return GapSeverityEnum.MEDIUM
        else:
            return GapSeverityEnum.LOW

    def _calculate_compliance_scores(
        self,
        organization_id: UUID,
    ) -> List[ComplianceScoreResponse]:
        """Calculate compliance scores by framework.

        Args:
            organization_id: Organization ID

        Returns:
            List of compliance scores by framework
        """
        scores = []

        # Get all frameworks
        frameworks = [
            FrameworkEnum.DORA_A,
            FrameworkEnum.DORA_B,
            FrameworkEnum.SOX,
            FrameworkEnum.BMR,
            FrameworkEnum.IOSCO,
            FrameworkEnum.NIST,
            FrameworkEnum.APPHEALTH,
        ]

        for framework in frameworks:
            score = self._calculate_framework_score(organization_id, framework)
            if score:
                scores.append(score)

        return scores

    def _calculate_framework_score(
        self,
        organization_id: UUID,
        framework: FrameworkEnum,
    ) -> ComplianceScoreResponse:
        """Calculate compliance score for a framework.

        Args:
            organization_id: Organization ID
            framework: Framework to calculate score for

        Returns:
            Compliance score response
        """
        from datetime import datetime

        # Get all checklist items for framework
        checklist_items = self.regulation_repository.list_by_framework(
            framework, skip=0, limit=10000
        )

        if not checklist_items:
            return None

        # Count compliance states by status
        compliant_count = 0
        partially_compliant_count = 0
        non_compliant_count = 0
        not_applicable_count = 0

        for item in checklist_items:
            state = self.compliance_repository.get_by_organization_and_checklist(
                organization_id, item.id
            )

            if not state:
                # If no state exists, assume not applicable
                not_applicable_count += 1
            elif state.status == ComplianceStatusEnum.COMPLIANT:
                compliant_count += 1
            elif state.status == ComplianceStatusEnum.PARTIALLY_COMPLIANT:
                partially_compliant_count += 1
            elif state.status == ComplianceStatusEnum.NON_COMPLIANT:
                non_compliant_count += 1
            elif state.status == ComplianceStatusEnum.NOT_APPLICABLE:
                not_applicable_count += 1

        # Calculate score
        total_applicable = (
            compliant_count + partially_compliant_count + non_compliant_count
        )

        if total_applicable == 0:
            score = 0.0
        else:
            score = (
                (compliant_count + (partially_compliant_count * 0.5)) / total_applicable
            ) * 100

        return ComplianceScoreResponse(
            framework=framework.value,
            score=round(score, 2),
            compliant_count=compliant_count,
            partially_compliant_count=partially_compliant_count,
            non_compliant_count=non_compliant_count,
            not_applicable_count=not_applicable_count,
            total_applicable=total_applicable,
            calculated_at=datetime.utcnow(),
        )
