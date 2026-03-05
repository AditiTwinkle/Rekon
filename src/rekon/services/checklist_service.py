"""Checklist service for business logic."""

import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from rekon.db.repositories.checklist import (
    ChecklistRepository,
    ChecklistItemRepository,
)
from rekon.domain.models.checklist import (
    ChecklistCreate,
    ChecklistItemCreate,
    ChecklistItemUpdate,
    ChecklistResponse,
    ChecklistItemResponse,
    FrameworkEnum,
)

logger = logging.getLogger(__name__)


class ChecklistService:
    """Service for checklist operations."""

    def __init__(self, db: Session):
        """Initialize service.

        Args:
            db: Database session
        """
        self.db = db
        self.checklist_repo = ChecklistRepository(db)
        self.item_repo = ChecklistItemRepository(db)

    def create_checklist(self, checklist: ChecklistCreate) -> ChecklistResponse:
        """Create a new checklist.

        Args:
            checklist: Checklist data

        Returns:
            Created checklist response
        """
        db_checklist = self.checklist_repo.create(checklist)
        logger.info(f"Created checklist for {checklist.framework}")
        return ChecklistResponse.from_orm(db_checklist)

    def create_checklist_item(
        self,
        item: ChecklistItemCreate,
    ) -> ChecklistItemResponse:
        """Create a new checklist item.

        Args:
            item: Checklist item data

        Returns:
            Created checklist item response
        """
        db_item = self.item_repo.create(item)
        logger.info(f"Created checklist item: {item.requirement_text[:50]}")
        return ChecklistItemResponse.from_orm(db_item)

    def get_checklist(self, checklist_id: UUID) -> Optional[ChecklistResponse]:
        """Get checklist by ID.

        Args:
            checklist_id: Checklist ID

        Returns:
            Checklist response or None
        """
        checklist = self.checklist_repo.get_by_id(checklist_id)
        if not checklist:
            return None
        return ChecklistResponse.from_orm(checklist)

    def get_latest_checklist_by_framework(
        self,
        framework: FrameworkEnum,
    ) -> Optional[ChecklistResponse]:
        """Get latest checklist for framework.

        Args:
            framework: Framework to filter by

        Returns:
            Latest checklist or None
        """
        checklist = self.checklist_repo.get_latest_by_framework(framework)
        if not checklist:
            return None
        return ChecklistResponse.from_orm(checklist)

    def list_checklists_by_framework(
        self,
        framework: FrameworkEnum,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ChecklistResponse]:
        """List checklists by framework.

        Args:
            framework: Framework to filter by
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            List of checklist responses
        """
        checklists = self.checklist_repo.list_by_framework(framework, skip, limit)
        return [ChecklistResponse.from_orm(c) for c in checklists]

    def list_checklist_items_by_framework(
        self,
        framework: FrameworkEnum,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ChecklistItemResponse]:
        """List checklist items by framework.

        Args:
            framework: Framework to filter by
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            List of checklist item responses
        """
        items = self.item_repo.list_by_framework(framework, skip, limit)
        return [ChecklistItemResponse.from_orm(i) for i in items]

    def get_checklist_item_count(self, framework: FrameworkEnum) -> int:
        """Get count of checklist items for framework.

        Args:
            framework: Framework to count

        Returns:
            Number of items
        """
        return self.item_repo.count_by_framework(framework)

    def update_checklist_item(
        self,
        item_id: UUID,
        updates: ChecklistItemUpdate,
    ) -> Optional[ChecklistItemResponse]:
        """Update a checklist item with customization tracking.

        Args:
            item_id: Item ID
            updates: Update data

        Returns:
            Updated checklist item response or None
        """
        update_dict = updates.dict(exclude_unset=True)
        if not update_dict:
            return None

        db_item = self.item_repo.update(item_id, update_dict)
        if not db_item:
            return None

        logger.info(f"Updated checklist item {item_id} with customizations")
        return ChecklistItemResponse.from_orm(db_item)

    def get_customization_history(self, item_id: UUID) -> Optional[list]:
        """Get customization history for a checklist item.

        Args:
            item_id: Item ID

        Returns:
            Customization history or None
        """
        item = self.item_repo.get_by_id(item_id)
        if not item:
            return None

        return item.customization_history or []

    def regenerate_checklist_preserving_customizations(
        self,
        checklist_id: UUID,
        new_items: list,
    ) -> Optional[ChecklistResponse]:
        """Regenerate checklist while preserving customizations.

        Args:
            checklist_id: Checklist ID
            new_items: New checklist items from regeneration

        Returns:
            Updated checklist response or None
        """
        checklist = self.checklist_repo.get_by_id(checklist_id)
        if not checklist:
            return None

        # Get existing customized items
        existing_items = self.item_repo.list_by_framework(checklist.framework)
        customized_items = {
            item.id: item for item in existing_items if item.is_customized
        }

        # Preserve customizations by matching on regulation_id and domain
        for new_item in new_items:
            for existing_item in existing_items:
                if (existing_item.regulation_id == new_item.get("regulation_id") and
                    existing_item.domain == new_item.get("domain") and
                    existing_item.is_customized):
                    # Preserve customized fields
                    new_item["requirement_text"] = existing_item.requirement_text
                    new_item["priority"] = existing_item.priority
                    new_item["evidence_requirements"] = existing_item.evidence_requirements
                    break

        # Increment version
        updated_checklist = self.checklist_repo.increment_version(checklist_id)
        logger.info(f"Regenerated checklist {checklist_id} preserving customizations")
        return ChecklistResponse.from_orm(updated_checklist) if updated_checklist else None
