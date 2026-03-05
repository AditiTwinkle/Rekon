"""Gap repository for database operations."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from rekon.db.schemas.gap import ComplianceGap
from rekon.domain.models.gap import ComplianceGapCreate, GapSeverityEnum, GapStatusEnum


class GapRepository:
    """Repository for gap operations."""

    def __init__(self, db: Session):
        """Initialize repository.

        Args:
            db: Database session
        """
        self.db = db

    def create(self, gap: ComplianceGapCreate) -> ComplianceGap:
        """Create a new gap.

        Args:
            gap: Gap data to create

        Returns:
            Created gap
        """
        db_gap = ComplianceGap(
            organization_id=gap.organization_id,
            checklist_item_id=gap.checklist_item_id,
            gap_type=gap.gap_type,
            severity=gap.severity,
            description=gap.description,
            root_cause=gap.root_cause,
            identified_by=gap.identified_by,
        )
        self.db.add(db_gap)
        self.db.commit()
        self.db.refresh(db_gap)
        return db_gap

    def get_by_id(self, gap_id: UUID) -> Optional[ComplianceGap]:
        """Get gap by ID.

        Args:
            gap_id: Gap ID

        Returns:
            Gap or None if not found
        """
        return self.db.query(ComplianceGap).filter(ComplianceGap.id == gap_id).first()

    def list_by_organization(
        self,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ComplianceGap]:
        """List gaps by organization.

        Args:
            organization_id: Organization ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of gaps
        """
        return (
            self.db.query(ComplianceGap)
            .filter(ComplianceGap.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_organization_and_status(
        self,
        organization_id: UUID,
        status: GapStatusEnum,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ComplianceGap]:
        """List gaps by organization and status.

        Args:
            organization_id: Organization ID
            status: Gap status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of gaps
        """
        return (
            self.db.query(ComplianceGap)
            .filter(
                ComplianceGap.organization_id == organization_id,
                ComplianceGap.status == status,
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_organization_and_severity(
        self,
        organization_id: UUID,
        severity: GapSeverityEnum,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ComplianceGap]:
        """List gaps by organization and severity.

        Args:
            organization_id: Organization ID
            severity: Gap severity
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of gaps
        """
        return (
            self.db.query(ComplianceGap)
            .filter(
                ComplianceGap.organization_id == organization_id,
                ComplianceGap.severity == severity,
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_organization(self, organization_id: UUID) -> int:
        """Count gaps by organization.

        Args:
            organization_id: Organization ID

        Returns:
            Number of gaps
        """
        return self.db.query(ComplianceGap).filter(
            ComplianceGap.organization_id == organization_id
        ).count()

    def count_by_organization_and_status(
        self,
        organization_id: UUID,
        status: GapStatusEnum,
    ) -> int:
        """Count gaps by organization and status.

        Args:
            organization_id: Organization ID
            status: Gap status

        Returns:
            Number of gaps
        """
        return self.db.query(ComplianceGap).filter(
            ComplianceGap.organization_id == organization_id,
            ComplianceGap.status == status,
        ).count()

    def update(self, gap_id: UUID, **kwargs) -> Optional[ComplianceGap]:
        """Update a gap.

        Args:
            gap_id: Gap ID
            **kwargs: Fields to update

        Returns:
            Updated gap or None if not found
        """
        gap = self.get_by_id(gap_id)
        if not gap:
            return None

        for key, value in kwargs.items():
            if hasattr(gap, key):
                setattr(gap, key, value)

        self.db.commit()
        self.db.refresh(gap)
        return gap
