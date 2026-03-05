"""Unit tests for regulation service."""

import pytest
from uuid import uuid4
from datetime import datetime

from sqlalchemy.orm import Session

from rekon.domain.models.regulation import (
    RegulationCreate,
    RegulationResponse,
    FrameworkEnum,
)
from rekon.services.regulation_service import RegulationService
from rekon.db.schemas.regulation import Regulation


@pytest.fixture
def regulation_service(db_session: Session) -> RegulationService:
    """Create regulation service instance."""
    return RegulationService(db_session)


@pytest.fixture
def sample_regulation_create() -> RegulationCreate:
    """Create sample regulation data."""
    return RegulationCreate(
        framework=FrameworkEnum.DORA_A,
        requirement_number="DORA-5.1",
        title="ICT Risk Management Framework",
        description="Financial entities shall establish and maintain an ICT risk management framework",
        source_url="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554",
        raw_content="Full regulatory text here...",
        content_hash="abc123def456",
    )


class TestRegulationServiceCreate:
    """Tests for regulation creation."""

    def test_create_regulation_success(
        self,
        regulation_service: RegulationService,
        sample_regulation_create: RegulationCreate,
    ):
        """Test successful regulation creation."""
        response = regulation_service.create_regulation(sample_regulation_create)

        assert response.framework == FrameworkEnum.DORA_A
        assert response.requirement_number == "DORA-5.1"
        assert response.title == "ICT Risk Management Framework"
        assert response.content_hash == "abc123def456"
        assert response.version == 1

    def test_create_regulation_duplicate_hash(
        self,
        regulation_service: RegulationService,
        sample_regulation_create: RegulationCreate,
    ):
        """Test that creating regulation with duplicate hash raises error."""
        # Create first regulation
        regulation_service.create_regulation(sample_regulation_create)

        # Try to create another with same hash
        with pytest.raises(ValueError, match="already exists"):
            regulation_service.create_regulation(sample_regulation_create)


class TestRegulationServiceRetrieval:
    """Tests for regulation retrieval."""

    def test_get_regulation_by_id(
        self,
        regulation_service: RegulationService,
        sample_regulation_create: RegulationCreate,
    ):
        """Test retrieving regulation by ID."""
        created = regulation_service.create_regulation(sample_regulation_create)
        retrieved = regulation_service.get_regulation(created.regulation_id)

        assert retrieved is not None
        assert retrieved.regulation_id == created.regulation_id
        assert retrieved.framework == FrameworkEnum.DORA_A

    def test_get_regulation_not_found(self, regulation_service: RegulationService):
        """Test retrieving non-existent regulation returns None."""
        result = regulation_service.get_regulation(uuid4())
        assert result is None

    def test_get_regulation_by_hash(
        self,
        regulation_service: RegulationService,
        sample_regulation_create: RegulationCreate,
    ):
        """Test retrieving regulation by content hash."""
        regulation_service.create_regulation(sample_regulation_create)
        retrieved = regulation_service.get_regulation_by_hash("abc123def456")

        assert retrieved is not None
        assert retrieved.content_hash == "abc123def456"

    def test_get_regulation_by_hash_not_found(
        self, regulation_service: RegulationService
    ):
        """Test retrieving regulation by non-existent hash returns None."""
        result = regulation_service.get_regulation_by_hash("nonexistent")
        assert result is None


class TestRegulationServiceListing:
    """Tests for regulation listing."""

    def test_list_regulations_by_framework(
        self,
        regulation_service: RegulationService,
        sample_regulation_create: RegulationCreate,
    ):
        """Test listing regulations by framework."""
        regulation_service.create_regulation(sample_regulation_create)

        results = regulation_service.list_regulations_by_framework(FrameworkEnum.DORA_A)

        assert len(results) == 1
        assert results[0].framework == FrameworkEnum.DORA_A

    def test_list_regulations_by_framework_empty(
        self, regulation_service: RegulationService
    ):
        """Test listing regulations for framework with no regulations."""
        results = regulation_service.list_regulations_by_framework(FrameworkEnum.SOX)
        assert len(results) == 0

    def test_list_all_regulations(
        self,
        regulation_service: RegulationService,
        sample_regulation_create: RegulationCreate,
    ):
        """Test listing all regulations."""
        regulation_service.create_regulation(sample_regulation_create)

        results = regulation_service.list_all_regulations()

        assert len(results) >= 1

    def test_list_regulations_pagination(
        self,
        regulation_service: RegulationService,
        sample_regulation_create: RegulationCreate,
    ):
        """Test pagination in regulation listing."""
        # Create multiple regulations
        for i in range(5):
            reg = RegulationCreate(
                framework=FrameworkEnum.DORA_A,
                requirement_number=f"DORA-{i}",
                title=f"Requirement {i}",
                description="Test",
                source_url="https://example.com",
                raw_content="Content",
                content_hash=f"hash{i}",
            )
            regulation_service.create_regulation(reg)

        # Test pagination
        page1 = regulation_service.list_all_regulations(skip=0, limit=2)
        page2 = regulation_service.list_all_regulations(skip=2, limit=2)

        assert len(page1) == 2
        assert len(page2) == 2
        assert page1[0].regulation_id != page2[0].regulation_id


class TestRegulationServiceCounting:
    """Tests for regulation counting."""

    def test_get_framework_count(
        self,
        regulation_service: RegulationService,
        sample_regulation_create: RegulationCreate,
    ):
        """Test counting regulations by framework."""
        regulation_service.create_regulation(sample_regulation_create)

        count = regulation_service.get_framework_count(FrameworkEnum.DORA_A)

        assert count == 1

    def test_get_framework_count_empty(self, regulation_service: RegulationService):
        """Test counting regulations for framework with no regulations."""
        count = regulation_service.get_framework_count(FrameworkEnum.SOX)
        assert count == 0

    def test_get_total_count(
        self,
        regulation_service: RegulationService,
        sample_regulation_create: RegulationCreate,
    ):
        """Test counting all regulations."""
        regulation_service.create_regulation(sample_regulation_create)

        count = regulation_service.get_total_count()

        assert count >= 1


class TestRegulationServiceChecks:
    """Tests for regulation existence checks."""

    def test_check_regulation_exists_by_hash_true(
        self,
        regulation_service: RegulationService,
        sample_regulation_create: RegulationCreate,
    ):
        """Test checking if regulation exists by hash."""
        regulation_service.create_regulation(sample_regulation_create)

        exists = regulation_service.check_regulation_exists_by_hash("abc123def456")

        assert exists is True

    def test_check_regulation_exists_by_hash_false(
        self, regulation_service: RegulationService
    ):
        """Test checking if non-existent regulation exists by hash."""
        exists = regulation_service.check_regulation_exists_by_hash("nonexistent")
        assert exists is False
