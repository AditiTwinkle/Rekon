"""Compliance state repository for database operations."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from rekon.db.schemas.compliance_state import ComplianceState
from rekon.domain.models.compliance_state import ComplianceStateCreate, ComplianceStatusEnum


class ComplianceStateRepository:
    """Repository for compliance state operations."""

    def __init__(self, db: Session):
        """Initialize repository.

        Args:
            db: Database session
        """
        self.db = db

    def create(self, state: ComplianceStateCreate) -> ComplianceState:
        """Create a new compliance state.

        Args:
            state: Compliance state data to create

        Returns:
            Created compliance state
        """
        db_state = ComplianceState(
            organization_id=state.organization_id,
            checklist_item_id=state.checklist_item_id,
            status=state.status,
            notes=state.notes,
            assessed_by=state.assessed_by,
        )
        self.db.add(db_state)
        self.db.commit()
        self.db.refresh(db_state)
        return db_state

    def get_by_id(self, state_id: UUID) -> Optional[ComplianceState]:
        """Get compliance state by ID.

        Args:
            state_id: Compliance state ID

        Returns:
            Compliance state or None if not found
        """
        return self.db.query(ComplianceState).filter(ComplianceState.id == state_id).first()

    def get_by_organization_and_checklist(
        self,
        organization_id: UUID,
        checklist_item_id: UUID,
    ) -> Optional[ComplianceState]:
        """Get compliance state by organization and checklist item.

        Args:
            organization_id: Organization ID
            checklist_item_id: Checklist item ID

        Returns:
            Compliance state or None if not found
        """
        return self.db.query(ComplianceState).filter(
            ComplianceState.organization_id == organization_id,
            ComplianceState.checklist_item_id == checklist_item_id,
        ).first()

    def list_by_organization(
        self,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ComplianceState]:
        """List compliance states by organization.

        Args:
            organization_id: Organization ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of compliance states
        """
        return (
            self.db.query(ComplianceState)
            .filter(ComplianceState.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_organization_and_status(
        self,
        organization_id: UUID,
        status: ComplianceStatusEnum,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ComplianceState]:
        """List compliance states by organization and status.

        Args:
            organization_id: Organization ID
            status: Compliance status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of compliance states
        """
        return (
            self.db.query(ComplianceState)
            .filter(
                ComplianceState.organization_id == organization_id,
                ComplianceState.status == status,
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_organization(self, organization_id: UUID) -> int:
        """Count compliance states by organization.

        Args:
            organization_id: Organization ID

        Returns:
            Number of compliance states
        """
        return self.db.query(ComplianceState).filter(
            ComplianceState.organization_id == organization_id
        ).count()

    def count_by_organization_and_status(
        self,
        organization_id: UUID,
        status: ComplianceStatusEnum,
    ) -> int:
        """Count compliance states by organization and status.

        Args:
            organization_id: Organization ID
            status: Compliance status

        Returns:
            Number of compliance states
        """
        return self.db.query(ComplianceState).filter(
            ComplianceState.organization_id == organization_id,
            ComplianceState.status == status,
        ).count()

    def update(self, state_id: UUID, **kwargs) -> Optional[ComplianceState]:
        """Update a compliance state.

        Args:
            state_id: Compliance state ID
            **kwargs: Fields to update

        Returns:
            Updated compliance state or None if not found
        """
        state = self.get_by_id(state_id)
        if not state:
            return None

        for key, value in kwargs.items():
            if hasattr(state, key):
                setattr(state, key, value)

        self.db.commit()
        self.db.refresh(state)
        return state

    def get_status_counts(self, organization_id: UUID) -> dict:
        """Get counts of compliance states by status.

        Args:
            organization_id: Organization ID

        Returns:
            Dictionary with status counts
        """
        results = (
            self.db.query(
                ComplianceState.status,
                func.count(ComplianceState.id).label("count"),
            )
            .filter(ComplianceState.organization_id == organization_id)
            .group_by(ComplianceState.status)
            .all()
        )

        counts = {
            ComplianceStatusEnum.COMPLIANT: 0,
            ComplianceStatusEnum.PARTIALLY_COMPLIANT: 0,
            ComplianceStatusEnum.NON_COMPLIANT: 0,
            ComplianceStatusEnum.NOT_APPLICABLE: 0,
        }

        for status, count in results:
            counts[status] = count

        return counts
