"""Evidence repository for database operations."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from rekon.db.schemas.evidence import Evidence
from rekon.domain.models.evidence import (
    EvidenceCreate,
    EvidenceUpdate,
    EvidenceAccessActionEnum,
)


class EvidenceRepository:
    """Repository for evidence database operations."""

    def __init__(self, db: Session):
        """Initialize repository.

        Args:
            db: Database session
        """
        self.db = db

    def create(self, evidence: EvidenceCreate, organization_id: UUID) -> Evidence:
        """Create new evidence record.

        Args:
            evidence: Evidence creation data
            organization_id: Organization ID

        Returns:
            Created evidence record
        """
        db_evidence = Evidence(
            organization_id=organization_id,
            checklist_item_id=evidence.checklist_item_id,
            file_name=evidence.file_name,
            file_type=evidence.file_type,
            file_path=evidence.file_path,
            file_hash=evidence.file_hash,
            file_size=evidence.file_size,
            upload_timestamp=datetime.utcnow(),
            uploaded_by=evidence.uploaded_by,
            expiration_date=evidence.expiration_date,
            retention_policy=evidence.retention_policy,
            access_log=[],
        )
        self.db.add(db_evidence)
        self.db.commit()
        self.db.refresh(db_evidence)
        return db_evidence

    def get_by_id(self, evidence_id: UUID, organization_id: UUID) -> Optional[Evidence]:
        """Get evidence by ID.

        Args:
            evidence_id: Evidence ID
            organization_id: Organization ID

        Returns:
            Evidence record or None
        """
        return self.db.query(Evidence).filter(
            Evidence.evidence_id == evidence_id,
            Evidence.organization_id == organization_id,
        ).first()

    def list_by_checklist_item(
        self,
        checklist_item_id: UUID,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Evidence], int]:
        """List evidence by checklist item.

        Args:
            checklist_item_id: Checklist item ID
            organization_id: Organization ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (evidence list, total count)
        """
        query = self.db.query(Evidence).filter(
            Evidence.checklist_item_id == checklist_item_id,
            Evidence.organization_id == organization_id,
        )
        total = query.count()
        records = query.offset(skip).limit(limit).all()
        return records, total

    def list_by_organization(
        self,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Evidence], int]:
        """List evidence by organization.

        Args:
            organization_id: Organization ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (evidence list, total count)
        """
        query = self.db.query(Evidence).filter(
            Evidence.organization_id == organization_id,
        )
        total = query.count()
        records = query.offset(skip).limit(limit).all()
        return records, total

    def get_by_hash(self, file_hash: str, organization_id: UUID) -> Optional[Evidence]:
        """Get evidence by file hash.

        Args:
            file_hash: File hash
            organization_id: Organization ID

        Returns:
            Evidence record or None
        """
        return self.db.query(Evidence).filter(
            Evidence.file_hash == file_hash,
            Evidence.organization_id == organization_id,
        ).first()

    def update(
        self,
        evidence_id: UUID,
        organization_id: UUID,
        update_data: EvidenceUpdate,
    ) -> Optional[Evidence]:
        """Update evidence record.

        Args:
            evidence_id: Evidence ID
            organization_id: Organization ID
            update_data: Update data

        Returns:
            Updated evidence record or None
        """
        evidence = self.get_by_id(evidence_id, organization_id)
        if not evidence:
            return None

        if update_data.expiration_date is not None:
            evidence.expiration_date = update_data.expiration_date
        if update_data.retention_policy is not None:
            evidence.retention_policy = update_data.retention_policy

        evidence.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(evidence)
        return evidence

    def add_access_log(
        self,
        evidence_id: UUID,
        organization_id: UUID,
        user_id: UUID,
        action: EvidenceAccessActionEnum,
    ) -> Optional[Evidence]:
        """Add access log entry to evidence.

        Args:
            evidence_id: Evidence ID
            organization_id: Organization ID
            user_id: User ID
            action: Access action

        Returns:
            Updated evidence record or None
        """
        evidence = self.get_by_id(evidence_id, organization_id)
        if not evidence:
            return None

        access_entry = {
            "user_id": str(user_id),
            "access_time": datetime.utcnow().isoformat(),
            "action": action.value,
        }

        if evidence.access_log is None:
            evidence.access_log = []
        evidence.access_log.append(access_entry)

        evidence.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(evidence)
        return evidence

    def delete(self, evidence_id: UUID, organization_id: UUID) -> bool:
        """Delete evidence record.

        Args:
            evidence_id: Evidence ID
            organization_id: Organization ID

        Returns:
            True if deleted, False if not found
        """
        evidence = self.get_by_id(evidence_id, organization_id)
        if not evidence:
            return False

        self.db.delete(evidence)
        self.db.commit()
        return True

    def list_expired(self, organization_id: UUID) -> List[Evidence]:
        """List expired evidence.

        Args:
            organization_id: Organization ID

        Returns:
            List of expired evidence records
        """
        now = datetime.utcnow()
        return self.db.query(Evidence).filter(
            Evidence.organization_id == organization_id,
            Evidence.expiration_date <= now,
        ).all()

    def list_expiring_soon(
        self,
        organization_id: UUID,
        days_threshold: int = 30,
    ) -> List[Evidence]:
        """List evidence expiring soon.

        Args:
            organization_id: Organization ID
            days_threshold: Number of days to look ahead

        Returns:
            List of evidence expiring soon
        """
        from datetime import timedelta

        now = datetime.utcnow()
        threshold = now + timedelta(days=days_threshold)

        return self.db.query(Evidence).filter(
            Evidence.organization_id == organization_id,
            Evidence.expiration_date > now,
            Evidence.expiration_date <= threshold,
        ).all()
