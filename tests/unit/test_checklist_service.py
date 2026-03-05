"""Unit tests for checklist service."""

import pytest
from uuid import uuid4
from datetime import datetime

from sqlalchemy.orm import Session

from rekon.domain.models.checklist import (
    ChecklistCreate,
    ChecklistItemCreate,
    ChecklistItemUpdate,
    ChecklistResponse,
    ChecklistItemResponse,
    FrameworkEnum,
    PriorityEnum,
)
from rekon.domain.models.regulation import RegulationCreate
from rekon.services.checklist_service import ChecklistService
from rekon.services.regulation_service import RegulationService


@pytest.fixture
def regulation_service(db_session: Session) -> RegulationService:
    """Create regulation service instance."""
    return RegulationService(db_session)


@pytest.fixture
def checklist_service(db_session: Session) -> ChecklistService:
    """Create checklist service instance."""
    return ChecklistService(db_session)


@pytest.fixture
def sample_regulation(regulation_service: RegulationService) -> RegulationCreate:
    """Create sample regulation."""
    reg = RegulationCreate(
        framework=FrameworkEnum.DORA_A,
        requirement_number="DORA-5.1",
        title="ICT Risk Management Framework",
        description="Financial entities shall establish and maintain an ICT risk management framework",
        source_url="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554",
        raw_content="Full regulatory text here...",
        content_hash="abc123def456",
    )
    return regulation_service.create_regulation(reg)


@pytest.fixture
def sample_checklist_item(sample_regulation) -> ChecklistItemCreate:
    """Create sample checklist item."""
    return ChecklistItemCreate(
        regulation_id=sample_regulation.regulation_id,
        framework=FrameworkEnum.DORA_A,
        domain="ICT Risk Management",
        category="Framework",
        requirement_text="Establish ICT risk management framework",
        priority=PriorityEnum.CRITICAL,
        evidence_requirements={
            "documentation": "ICT Risk Management Policy",
            "testing": "Framework assessment",
        },
        regulatory_citation="DORA Article 5(1)",
    )


@pytest.fixture
def sample_checklist(checklist_service: ChecklistService) -> ChecklistResponse:
    """Create sample checklist."""
    checklist = ChecklistCreate(
        framework=FrameworkEnum.DORA_A,
        title="DORA Category A Checklist",
        description="Comprehensive checklist for DORA Category A requirements",
    )
    return checklist_service.create_checklist(checklist)


class TestChecklistServiceCreate:
    """Tests for checklist creation."""

    def test_create_checklist_success(
        self,
        checklist_service: ChecklistService,
    ):
        """Test successful checklist creation."""
        checklist = ChecklistCreate(
            framework=FrameworkEnum.DORA_A,
            title="DORA Category A Checklist",
            description="Comprehensive checklist for DORA Category A requirements",
        )
        response = checklist_service.create_checklist(checklist)

        assert response.framework == FrameworkEnum.DORA_A
        assert response.title == "DORA Category A Checklist"
        assert response.version == 1
        assert response.item_count == 0

    def test_create_checklist_item_success(
        self,
        checklist_service: ChecklistService,
        sample_checklist_item: ChecklistItemCreate,
    ):
        """Test successful checklist item creation."""
        response = checklist_service.create_checklist_item(sample_checklist_item)

        assert response.framework == FrameworkEnum.DORA_A
        assert response.domain == "ICT Risk Management"
        assert response.priority == PriorityEnum.CRITICAL
        assert response.version == 1
        assert response.is_customized is False


class TestChecklistServiceRetrieval:
    """Tests for checklist retrieval."""

    def test_get_checklist_by_id(
        self,
        checklist_service: ChecklistService,
        sample_checklist: ChecklistResponse,
    ):
        """Test retrieving checklist by ID."""
        retrieved = checklist_service.get_checklist(sample_checklist.checklist_id)

        assert retrieved is not None
        assert retrieved.checklist_id == sample_checklist.checklist_id
        assert retrieved.framework == FrameworkEnum.DORA_A

    def test_get_checklist_not_found(self, checklist_service: ChecklistService):
        """Test retrieving non-existent checklist returns None."""
        result = checklist_service.get_checklist(uuid4())
        assert result is None

    def test_get_latest_checklist_by_framework(
        self,
        checklist_service: ChecklistService,
        sample_checklist: ChecklistResponse,
    ):
        """Test retrieving latest checklist for framework."""
        retrieved = checklist_service.get_latest_checklist_by_framework(
            FrameworkEnum.DORA_A
        )

        assert retrieved is not None
        assert retrieved.framework == FrameworkEnum.DORA_A

    def test_get_latest_checklist_by_framework_not_found(
        self, checklist_service: ChecklistService
    ):
        """Test retrieving latest checklist for framework with no checklists."""
        result = checklist_service.get_latest_checklist_by_framework(FrameworkEnum.SOX)
        assert result is None


class TestChecklistServiceListing:
    """Tests for checklist listing."""

    def test_list_checklists_by_framework(
        self,
        checklist_service: ChecklistService,
        sample_checklist: ChecklistResponse,
    ):
        """Test listing checklists by framework."""
        results = checklist_service.list_checklists_by_framework(FrameworkEnum.DORA_A)

        assert len(results) >= 1
        assert results[0].framework == FrameworkEnum.DORA_A

    def test_list_checklists_by_framework_empty(
        self, checklist_service: ChecklistService
    ):
        """Test listing checklists for framework with no checklists."""
        results = checklist_service.list_checklists_by_framework(FrameworkEnum.SOX)
        assert len(results) == 0

    def test_list_checklist_items_by_framework(
        self,
        checklist_service: ChecklistService,
        sample_checklist_item: ChecklistItemCreate,
    ):
        """Test listing checklist items by framework."""
        checklist_service.create_checklist_item(sample_checklist_item)

        results = checklist_service.list_checklist_items_by_framework(
            FrameworkEnum.DORA_A
        )

        assert len(results) >= 1
        assert results[0].framework == FrameworkEnum.DORA_A

    def test_list_checklist_items_by_framework_empty(
        self, checklist_service: ChecklistService
    ):
        """Test listing checklist items for framework with no items."""
        results = checklist_service.list_checklist_items_by_framework(FrameworkEnum.SOX)
        assert len(results) == 0


class TestChecklistServiceCounting:
    """Tests for checklist counting."""

    def test_get_checklist_item_count(
        self,
        checklist_service: ChecklistService,
        sample_checklist_item: ChecklistItemCreate,
    ):
        """Test counting checklist items by framework."""
        checklist_service.create_checklist_item(sample_checklist_item)

        count = checklist_service.get_checklist_item_count(FrameworkEnum.DORA_A)

        assert count >= 1

    def test_get_checklist_item_count_empty(self, checklist_service: ChecklistService):
        """Test counting checklist items for framework with no items."""
        count = checklist_service.get_checklist_item_count(FrameworkEnum.SOX)
        assert count == 0


class TestChecklistServiceCustomization:
    """Tests for checklist customization."""

    def test_update_checklist_item_success(
        self,
        checklist_service: ChecklistService,
        sample_checklist_item: ChecklistItemCreate,
    ):
        """Test successful checklist item update."""
        created = checklist_service.create_checklist_item(sample_checklist_item)

        updates = ChecklistItemUpdate(
            requirement_text="Updated requirement text",
            priority=PriorityEnum.HIGH,
        )
        updated = checklist_service.update_checklist_item(created.checklist_item_id, updates)

        assert updated is not None
        assert updated.requirement_text == "Updated requirement text"
        assert updated.priority == PriorityEnum.HIGH
        assert updated.is_customized is True

    def test_update_checklist_item_not_found(
        self, checklist_service: ChecklistService
    ):
        """Test updating non-existent checklist item returns None."""
        updates = ChecklistItemUpdate(requirement_text="Updated text")
        result = checklist_service.update_checklist_item(uuid4(), updates)
        assert result is None

    def test_update_checklist_item_partial(
        self,
        checklist_service: ChecklistService,
        sample_checklist_item: ChecklistItemCreate,
    ):
        """Test partial update of checklist item."""
        created = checklist_service.create_checklist_item(sample_checklist_item)

        updates = ChecklistItemUpdate(priority=PriorityEnum.LOW)
        updated = checklist_service.update_checklist_item(created.checklist_item_id, updates)

        assert updated is not None
        assert updated.priority == PriorityEnum.LOW
        assert updated.requirement_text == sample_checklist_item.requirement_text

    def test_get_customization_history(
        self,
        checklist_service: ChecklistService,
        sample_checklist_item: ChecklistItemCreate,
    ):
        """Test retrieving customization history."""
        created = checklist_service.create_checklist_item(sample_checklist_item)

        # Make updates
        updates = ChecklistItemUpdate(requirement_text="Updated text")
        checklist_service.update_checklist_item(created.checklist_item_id, updates)

        history = checklist_service.get_customization_history(created.checklist_item_id)

        assert history is not None
        assert len(history) >= 1
        assert "requirement_text" in history[0]["changes"]

    def test_get_customization_history_not_found(
        self, checklist_service: ChecklistService
    ):
        """Test retrieving customization history for non-existent item."""
        result = checklist_service.get_customization_history(uuid4())
        assert result is None

    def test_customization_history_tracks_changes(
        self,
        checklist_service: ChecklistService,
        sample_checklist_item: ChecklistItemCreate,
    ):
        """Test that customization history tracks all changes."""
        created = checklist_service.create_checklist_item(sample_checklist_item)

        # First update
        updates1 = ChecklistItemUpdate(priority=PriorityEnum.HIGH)
        checklist_service.update_checklist_item(created.checklist_item_id, updates1)

        # Second update
        updates2 = ChecklistItemUpdate(requirement_text="New text")
        checklist_service.update_checklist_item(created.checklist_item_id, updates2)

        history = checklist_service.get_customization_history(created.checklist_item_id)

        assert len(history) == 2
        assert "priority" in history[0]["changes"]
        assert "requirement_text" in history[1]["changes"]


class TestChecklistServiceRegeneration:
    """Tests for checklist regeneration with customization preservation."""

    def test_regenerate_checklist_preserving_customizations(
        self,
        checklist_service: ChecklistService,
        sample_checklist: ChecklistResponse,
        sample_checklist_item: ChecklistItemCreate,
    ):
        """Test regenerating checklist while preserving customizations."""
        # Create and customize an item
        created = checklist_service.create_checklist_item(sample_checklist_item)
        updates = ChecklistItemUpdate(requirement_text="Customized text")
        checklist_service.update_checklist_item(created.checklist_item_id, updates)

        # Prepare new items for regeneration
        new_items = [
            {
                "regulation_id": sample_checklist_item.regulation_id,
                "framework": FrameworkEnum.DORA_A,
                "domain": "ICT Risk Management",
                "category": "Framework",
                "requirement_text": "Original requirement text",
                "priority": PriorityEnum.CRITICAL,
                "evidence_requirements": {"test": "value"},
                "regulatory_citation": "DORA Article 5(1)",
            }
        ]

        # Regenerate
        result = checklist_service.regenerate_checklist_preserving_customizations(
            sample_checklist.checklist_id,
            new_items,
        )

        assert result is not None
        assert result.version == 2

    def test_regenerate_checklist_not_found(
        self, checklist_service: ChecklistService
    ):
        """Test regenerating non-existent checklist returns None."""
        result = checklist_service.regenerate_checklist_preserving_customizations(
            uuid4(),
            [],
        )
        assert result is None
