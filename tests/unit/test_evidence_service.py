"""Unit tests for evidence service."""

import hashlib
from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from rekon.services.evidence_service import EvidenceService
from rekon.domain.models.evidence import (
    EvidenceCreate,
    EvidenceUpdate,
    EvidenceTypeEnum,
    EvidenceAccessActionEnum,
)


@pytest.fixture
def evidence_service(db_session: Session) -> EvidenceService:
    """Create evidence service instance."""
    return EvidenceService(db_session)


@pytest.fixture
def test_data():
    """Create test data."""
    return {
        "organization_id": uuid4(),
        "checklist_item_id": uuid4(),
        "user_id": uuid4(),
        "file_name": "test_evidence.pdf",
        "file_type": EvidenceTypeEnum.DOCUMENT,
        "file_content": b"Test evidence content",
    }


class TestEvidenceUpload:
    """Tests for evidence upload functionality."""

    def test_upload_evidence_success(self, evidence_service, test_data):
        """Test successful evidence upload."""
        response = evidence_service.upload_evidence(
            organization_id=test_data["organization_id"],
            checklist_item_id=test_data["checklist_item_id"],
            file_name=test_data["file_name"],
            file_type=test_data["file_type"],
            file_content=test_data["file_content"],
            uploaded_by=test_data["user_id"],
        )

        assert response.evidence_id is not None
        assert response.file_name == test_data["file_name"]
        assert response.file_type == test_data["file_type"]
        assert response.uploaded_by == test_data["user_id"]
        assert response.organization_id == test_data["organization_id"]

    def test_upload_evidence_with_expiration(self, evidence_service, test_data):
        """Test evidence upload with expiration date."""
        expiration = datetime.utcnow() + timedelta(days=30)

        response = evidence_service.upload_evidence(
            organization_id=test_data["organization_id"],
            checklist_item_id=test_data["checklist_item_id"],
            file_name=test_data["file_name"],
            file_type=test_data["file_type"],
            file_content=test_data["file_content"],
            uploaded_by=test_data["user_id"],
            expiration_date=expiration,
        )

        assert response.expiration_date is not None
        assert response.expiration_date.date() == expiration.date()

    def test_upload_duplicate_evidence_fails(self, evidence_service, test_data):
        """Test that uploading duplicate evidence fails."""
        # Upload first time
        evidence_service.upload_evidence(
            organization_id=test_data["organization_id"],
            checklist_item_id=test_data["checklist_item_id"],
            file_name=test_data["file_name"],
            file_type=test_data["file_type"],
            file_content=test_data["file_content"],
            uploaded_by=test_data["user_id"],
        )

        # Try to upload same content again
        with pytest.raises(ValueError, match="already exists"):
            evidence_service.upload_evidence(
                organization_id=test_data["organization_id"],
                checklist_item_id=test_data["checklist_item_id"],
                file_name=test_data["file_name"],
                file_type=test_data["file_type"],
                file_content=test_data["file_content"],
                uploaded_by=test_data["user_id"],
            )

    def test_upload_evidence_calculates_hash(self, evidence_service, test_data):
        """Test that evidence upload calculates file hash."""
        response = evidence_service.upload_evidence(
            organization_id=test_data["organization_id"],
            checklist_item_id=test_data["checklist_item_id"],
            file_name=test_data["file_name"],
            file_type=test_data["file_type"],
            file_content=test_data["file_content"],
            uploaded_by=test_data["user_id"],
        )

        expected_hash = hashlib.sha256(test_data["file_content"]).hexdigest()
        assert response.file_hash == expected_hash


class TestEvidenceRetrieval:
    """Tests for evidence retrieval functionality."""

    def test_get_evidence_by_id(self, evidence_service, test_data):
        """Test retrieving evidence by ID."""
        uploaded = evidence_service.upload_evidence(
            organization_id=test_data["organization_id"],
            checklist_item_id=test_data["checklist_item_id"],
            file_name=test_data["file_name"],
            file_type=test_data["file_type"],
            file_content=test_data["file_content"],
            uploaded_by=test_data["user_id"],
        )

        retrieved = evidence_service.get_evidence(
            uploaded.evidence_id,
            test_data["organization_id"],
            test_data["user_id"],
        )

        assert retrieved.evidence_id == uploaded.evidence_id
        assert retrieved.file_name == uploaded.file_name

    def test_get_nonexistent_evidence_fails(self, evidence_service, test_data):
        """Test that retrieving nonexistent evidence fails."""
        with pytest.raises(ValueError, match="not found"):
            evidence_service.get_evidence(
                uuid4(),
                test_data["organization_id"],
                test_data["user_id"],
            )

    def test_list_evidence_by_checklist_item(self, evidence_service, test_data):
        """Test listing evidence by checklist item."""
        # Upload multiple evidence items
        for i in range(3):
            evidence_service.upload_evidence(
                organization_id=test_data["organization_id"],
                checklist_item_id=test_data["checklist_item_id"],
                file_name=f"evidence_{i}.pdf",
                file_type=test_data["file_type"],
                file_content=f"Content {i}".encode(),
                uploaded_by=test_data["user_id"],
            )

        evidence_list, total = evidence_service.list_evidence_by_checklist_item(
            test_data["checklist_item_id"],
            test_data["organization_id"],
        )

        assert len(evidence_list) == 3
        assert total == 3

    def test_list_evidence_by_organization(self, evidence_service, test_data):
        """Test listing evidence by organization."""
        # Upload evidence for different checklist items
        for i in range(2):
            evidence_service.upload_evidence(
                organization_id=test_data["organization_id"],
                checklist_item_id=uuid4(),
                file_name=f"evidence_{i}.pdf",
                file_type=test_data["file_type"],
                file_content=f"Content {i}".encode(),
                uploaded_by=test_data["user_id"],
            )

        evidence_list, total = evidence_service.list_evidence_by_organization(
            test_data["organization_id"],
        )

        assert len(evidence_list) == 2
        assert total == 2

    def test_list_evidence_pagination(self, evidence_service, test_data):
        """Test evidence listing with pagination."""
        # Upload 5 evidence items
        for i in range(5):
            evidence_service.upload_evidence(
                organization_id=test_data["organization_id"],
                checklist_item_id=test_data["checklist_item_id"],
                file_name=f"evidence_{i}.pdf",
                file_type=test_data["file_type"],
                file_content=f"Content {i}".encode(),
                uploaded_by=test_data["user_id"],
            )

        # Get first page
        page1, total = evidence_service.list_evidence_by_checklist_item(
            test_data["checklist_item_id"],
            test_data["organization_id"],
            skip=0,
            limit=2,
        )

        assert len(page1) == 2
        assert total == 5

        # Get second page
        page2, _ = evidence_service.list_evidence_by_checklist_item(
            test_data["checklist_item_id"],
            test_data["organization_id"],
            skip=2,
            limit=2,
        )

        assert len(page2) == 2


class TestEvidenceUpdate:
    """Tests for evidence update functionality."""

    def test_update_evidence_expiration(self, evidence_service, test_data):
        """Test updating evidence expiration date."""
        uploaded = evidence_service.upload_evidence(
            organization_id=test_data["organization_id"],
            checklist_item_id=test_data["checklist_item_id"],
            file_name=test_data["file_name"],
            file_type=test_data["file_type"],
            file_content=test_data["file_content"],
            uploaded_by=test_data["user_id"],
        )

        new_expiration = datetime.utcnow() + timedelta(days=60)
        update_data = EvidenceUpdate(expiration_date=new_expiration)

        updated = evidence_service.update_evidence(
            uploaded.evidence_id,
            test_data["organization_id"],
            update_data,
        )

        assert updated.expiration_date.date() == new_expiration.date()

    def test_update_evidence_retention_policy(self, evidence_service, test_data):
        """Test updating evidence retention policy."""
        uploaded = evidence_service.upload_evidence(
            organization_id=test_data["organization_id"],
            checklist_item_id=test_data["checklist_item_id"],
            file_name=test_data["file_name"],
            file_type=test_data["file_type"],
            file_content=test_data["file_content"],
            uploaded_by=test_data["user_id"],
        )

        update_data = EvidenceUpdate(retention_policy="7_years")

        updated = evidence_service.update_evidence(
            uploaded.evidence_id,
            test_data["organization_id"],
            update_data,
        )

        assert updated.retention_policy == "7_years"


class TestEvidenceExpiration:
    """Tests for evidence expiration functionality."""

    def test_get_expired_evidence(self, evidence_service, test_data):
        """Test retrieving expired evidence."""
        # Upload evidence that's already expired
        past_date = datetime.utcnow() - timedelta(days=1)
        evidence_service.upload_evidence(
            organization_id=test_data["organization_id"],
            checklist_item_id=test_data["checklist_item_id"],
            file_name="expired.pdf",
            file_type=test_data["file_type"],
            file_content=b"Expired content",
            uploaded_by=test_data["user_id"],
            expiration_date=past_date,
        )

        expired = evidence_service.get_expired_evidence(test_data["organization_id"])

        assert len(expired) == 1
        assert expired[0].file_name == "expired.pdf"

    def test_get_expiring_soon_evidence(self, evidence_service, test_data):
        """Test retrieving evidence expiring soon."""
        # Upload evidence expiring in 15 days
        future_date = datetime.utcnow() + timedelta(days=15)
        evidence_service.upload_evidence(
            organization_id=test_data["organization_id"],
            checklist_item_id=test_data["checklist_item_id"],
            file_name="expiring_soon.pdf",
            file_type=test_data["file_type"],
            file_content=b"Expiring soon content",
            uploaded_by=test_data["user_id"],
            expiration_date=future_date,
        )

        expiring = evidence_service.get_expiring_soon_evidence(
            test_data["organization_id"],
            days_threshold=30,
        )

        assert len(expiring) == 1
        assert expiring[0].file_name == "expiring_soon.pdf"


class TestEvidenceIntegrity:
    """Tests for evidence integrity verification."""

    def test_verify_evidence_integrity_success(self, evidence_service, test_data):
        """Test successful evidence integrity verification."""
        uploaded = evidence_service.upload_evidence(
            organization_id=test_data["organization_id"],
            checklist_item_id=test_data["checklist_item_id"],
            file_name=test_data["file_name"],
            file_type=test_data["file_type"],
            file_content=test_data["file_content"],
            uploaded_by=test_data["user_id"],
        )

        is_valid = evidence_service.verify_evidence_integrity(
            uploaded.evidence_id,
            test_data["organization_id"],
            test_data["file_content"],
        )

        assert is_valid is True

    def test_verify_evidence_integrity_failure(self, evidence_service, test_data):
        """Test evidence integrity verification failure."""
        uploaded = evidence_service.upload_evidence(
            organization_id=test_data["organization_id"],
            checklist_item_id=test_data["checklist_item_id"],
            file_name=test_data["file_name"],
            file_type=test_data["file_type"],
            file_content=test_data["file_content"],
            uploaded_by=test_data["user_id"],
        )

        is_valid = evidence_service.verify_evidence_integrity(
            uploaded.evidence_id,
            test_data["organization_id"],
            b"Different content",
        )

        assert is_valid is False


class TestEvidenceDeletion:
    """Tests for evidence deletion functionality."""

    def test_delete_evidence_success(self, evidence_service, test_data):
        """Test successful evidence deletion."""
        uploaded = evidence_service.upload_evidence(
            organization_id=test_data["organization_id"],
            checklist_item_id=test_data["checklist_item_id"],
            file_name=test_data["file_name"],
            file_type=test_data["file_type"],
            file_content=test_data["file_content"],
            uploaded_by=test_data["user_id"],
        )

        deleted = evidence_service.delete_evidence(
            uploaded.evidence_id,
            test_data["organization_id"],
            test_data["user_id"],
        )

        assert deleted is True

    def test_delete_nonexistent_evidence_fails(self, evidence_service, test_data):
        """Test that deleting nonexistent evidence fails."""
        deleted = evidence_service.delete_evidence(
            uuid4(),
            test_data["organization_id"],
            test_data["user_id"],
        )

        assert deleted is False
