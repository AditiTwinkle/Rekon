"""Evidence management service."""

import hashlib
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from rekon.db.repositories.evidence import EvidenceRepository
from rekon.domain.models.evidence import (
    EvidenceCreate,
    EvidenceResponse,
    EvidenceUpdate,
    EvidenceAccessActionEnum,
)


class EvidenceService:
    """Service for evidence management operations."""

    def __init__(self, db: Session):
        """Initialize service.

        Args:
            db: Database session
        """
        self.db = db
        self.repository = EvidenceRepository(db)

    def upload_evidence(
        self,
        organization_id: UUID,
        checklist_item_id: UUID,
        file_name: str,
        file_type: str,
        file_content: bytes,
        uploaded_by: UUID,
        expiration_date: Optional[datetime] = None,
        retention_policy: Optional[str] = None,
    ) -> EvidenceResponse:
        """Upload evidence file.

        Args:
            organization_id: Organization ID
            checklist_item_id: Checklist item ID
            file_name: File name
            file_type: File type
            file_content: File content bytes
            uploaded_by: User ID uploading the file
            expiration_date: Optional expiration date
            retention_policy: Optional retention policy

        Returns:
            Evidence response

        Raises:
            ValueError: If file validation fails
        """
        # Calculate file hash for integrity verification
        file_hash = hashlib.sha256(file_content).hexdigest()

        # Check for duplicate evidence
        existing = self.repository.get_by_hash(file_hash, organization_id)
        if existing:
            raise ValueError(f"Evidence with hash {file_hash} already exists")

        # In production, this would upload to S3
        # For now, we'll store the path as a reference
        file_path = f"s3://rekon-evidence/{organization_id}/{checklist_item_id}/{file_name}"

        # Create evidence record
        evidence_create = EvidenceCreate(
            checklist_item_id=checklist_item_id,
            file_name=file_name,
            file_type=file_type,
            file_path=file_path,
            file_hash=file_hash,
            file_size=len(file_content),
            uploaded_by=uploaded_by,
            expiration_date=expiration_date,
            retention_policy=retention_policy,
        )

        db_evidence = self.repository.create(evidence_create, organization_id)

        # Log the upload access
        self.repository.add_access_log(
            db_evidence.evidence_id,
            organization_id,
            uploaded_by,
            EvidenceAccessActionEnum.VIEW,
        )

        return self._to_response(db_evidence)

    def get_evidence(
        self,
        evidence_id: UUID,
        organization_id: UUID,
        user_id: UUID,
    ) -> EvidenceResponse:
        """Get evidence by ID.

        Args:
            evidence_id: Evidence ID
            organization_id: Organization ID
            user_id: User ID accessing the evidence

        Returns:
            Evidence response

        Raises:
            ValueError: If evidence not found
        """
        evidence = self.repository.get_by_id(evidence_id, organization_id)
        if not evidence:
            raise ValueError(f"Evidence {evidence_id} not found")

        # Log access
        self.repository.add_access_log(
            evidence_id,
            organization_id,
            user_id,
            EvidenceAccessActionEnum.VIEW,
        )

        return self._to_response(evidence)

    def list_evidence_by_checklist_item(
        self,
        checklist_item_id: UUID,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[EvidenceResponse], int]:
        """List evidence by checklist item.

        Args:
            checklist_item_id: Checklist item ID
            organization_id: Organization ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (evidence list, total count)
        """
        records, total = self.repository.list_by_checklist_item(
            checklist_item_id,
            organization_id,
            skip,
            limit,
        )
        return [self._to_response(r) for r in records], total

    def list_evidence_by_organization(
        self,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[EvidenceResponse], int]:
        """List evidence by organization.

        Args:
            organization_id: Organization ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (evidence list, total count)
        """
        records, total = self.repository.list_by_organization(
            organization_id,
            skip,
            limit,
        )
        return [self._to_response(r) for r in records], total

    def update_evidence(
        self,
        evidence_id: UUID,
        organization_id: UUID,
        update_data: EvidenceUpdate,
    ) -> EvidenceResponse:
        """Update evidence record.

        Args:
            evidence_id: Evidence ID
            organization_id: Organization ID
            update_data: Update data

        Returns:
            Updated evidence response

        Raises:
            ValueError: If evidence not found
        """
        evidence = self.repository.update(evidence_id, organization_id, update_data)
        if not evidence:
            raise ValueError(f"Evidence {evidence_id} not found")

        return self._to_response(evidence)

    def delete_evidence(
        self,
        evidence_id: UUID,
        organization_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Delete evidence record.

        Args:
            evidence_id: Evidence ID
            organization_id: Organization ID
            user_id: User ID deleting the evidence

        Returns:
            True if deleted, False if not found
        """
        # Log deletion access before deleting
        evidence = self.repository.get_by_id(evidence_id, organization_id)
        if evidence:
            self.repository.add_access_log(
                evidence_id,
                organization_id,
                user_id,
                EvidenceAccessActionEnum.DELETE,
            )

        return self.repository.delete(evidence_id, organization_id)

    def get_expired_evidence(
        self,
        organization_id: UUID,
    ) -> List[EvidenceResponse]:
        """Get expired evidence.

        Args:
            organization_id: Organization ID

        Returns:
            List of expired evidence
        """
        records = self.repository.list_expired(organization_id)
        return [self._to_response(r) for r in records]

    def get_expiring_soon_evidence(
        self,
        organization_id: UUID,
        days_threshold: int = 30,
    ) -> List[EvidenceResponse]:
        """Get evidence expiring soon.

        Args:
            organization_id: Organization ID
            days_threshold: Number of days to look ahead

        Returns:
            List of evidence expiring soon
        """
        records = self.repository.list_expiring_soon(organization_id, days_threshold)
        return [self._to_response(r) for r in records]

    def verify_evidence_integrity(
        self,
        evidence_id: UUID,
        organization_id: UUID,
        file_content: bytes,
    ) -> bool:
        """Verify evidence file integrity.

        Args:
            evidence_id: Evidence ID
            organization_id: Organization ID
            file_content: File content to verify

        Returns:
            True if hash matches, False otherwise

        Raises:
            ValueError: If evidence not found
        """
        evidence = self.repository.get_by_id(evidence_id, organization_id)
        if not evidence:
            raise ValueError(f"Evidence {evidence_id} not found")

        file_hash = hashlib.sha256(file_content).hexdigest()
        return file_hash == evidence.file_hash

    def generate_evidence_collection_package(
        self,
        checklist_item_id: UUID,
        organization_id: UUID,
    ) -> dict:
        """Generate evidence collection package for a requirement.

        Args:
            checklist_item_id: Checklist item ID
            organization_id: Organization ID

        Returns:
            Evidence collection package with metadata

        Raises:
            ValueError: If no evidence found
        """
        evidence_list, total = self.repository.list_by_checklist_item(
            checklist_item_id,
            organization_id,
            skip=0,
            limit=1000,
        )

        if not evidence_list:
            raise ValueError(f"No evidence found for checklist item {checklist_item_id}")

        package = {
            "checklist_item_id": str(checklist_item_id),
            "organization_id": str(organization_id),
            "generated_at": datetime.utcnow().isoformat(),
            "total_evidence": len(evidence_list),
            "total_size_bytes": sum(e.file_size for e in evidence_list),
            "evidence": [
                {
                    "evidence_id": str(e.evidence_id),
                    "file_name": e.file_name,
                    "file_type": e.file_type.value,
                    "file_size": e.file_size,
                    "file_hash": e.file_hash,
                    "upload_timestamp": e.upload_timestamp.isoformat(),
                    "uploaded_by": str(e.uploaded_by),
                    "expiration_date": e.expiration_date.isoformat() if e.expiration_date else None,
                }
                for e in evidence_list
            ],
        }

        return package

    def search_evidence_by_requirement(
        self,
        organization_id: UUID,
        requirement_text: str = None,
        file_type: str = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[EvidenceResponse], int]:
        """Search evidence by requirement criteria.

        Args:
            organization_id: Organization ID
            requirement_text: Optional requirement text to search
            file_type: Optional file type to filter
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (evidence list, total count)
        """
        # Get all evidence for organization
        records, total = self.repository.list_by_organization(
            organization_id,
            skip=0,
            limit=10000,
        )

        # Filter by file type if specified
        if file_type:
            records = [r for r in records if r.file_type.value == file_type]

        # Apply pagination
        filtered_records = records[skip : skip + limit]
        filtered_total = len(records)

        return [self._to_response(r) for r in filtered_records], filtered_total

    def _to_response(self, evidence) -> EvidenceResponse:
        """Convert evidence record to response model.

        Args:
            evidence: Evidence database record

        Returns:
            Evidence response model
        """
        return EvidenceResponse(
            evidence_id=evidence.evidence_id,
            organization_id=evidence.organization_id,
            checklist_item_id=evidence.checklist_item_id,
            file_name=evidence.file_name,
            file_type=evidence.file_type,
            file_path=evidence.file_path,
            file_hash=evidence.file_hash,
            file_size=evidence.file_size,
            upload_timestamp=evidence.upload_timestamp,
            uploaded_by=evidence.uploaded_by,
            expiration_date=evidence.expiration_date,
            retention_policy=evidence.retention_policy,
            access_log=evidence.access_log or [],
            created_at=evidence.created_at,
            updated_at=evidence.updated_at,
        )
