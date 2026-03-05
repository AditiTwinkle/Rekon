"""Checklist repository for database operations."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from rekon.db.schemas.checklist import ChecklistItem, Checklist
from rekon.domain.models.checklist import (
    ChecklistItemCreate,
    ChecklistCreate,
    FrameworkEnum,
)


class ChecklistItemRepository:
    """Repository for checklist item database operations."""

    def __init__(self, db: Session):
        """Initialize repository.

        Args:
            db: Database session
        """
        self.db = db

    def create(self, item: ChecklistItemCreate) -> ChecklistItem:
        """Create a new checklist item.

        Args:
            item: Checklist item data

        Returns:
            Created checklist item
        """
        db_item = ChecklistItem(
            regulation_id=item.regulation_id,
            framework=item.framework,
            domain=item.domain,
            category=item.category,
            requirement_text=item.requirement_text,
            priority=item.priority,
            evidence_requirements=item.evidence_requirements,
            regulatory_citation=item.regulatory_citation,
        )

        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)

        return db_item

    def get_by_id(self, item_id: UUID) -> Optional[ChecklistItem]:
        """Get checklist item by ID.

        Args:
            item_id: Item ID

        Returns:
            Checklist item or None
        """
        return self.db.query(ChecklistItem).filter(
            ChecklistItem.id == item_id
        ).first()

    def update(self, item_id: UUID, updates: dict) -> Optional[ChecklistItem]:
        """Update a checklist item.

        Args:
            item_id: Item ID
            updates: Dictionary of fields to update

        Returns:
            Updated checklist item or None
        """
        item = self.get_by_id(item_id)
        if not item:
            return None

        # Track customization history
        if not item.customization_history:
            item.customization_history = []

        # Record the change
        change_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "changes": {}
        }

        for key, value in updates.items():
            if hasattr(item, key):
                old_value = getattr(item, key)
                if old_value != value:
                    change_record["changes"][key] = {
                        "old": str(old_value),
                        "new": str(value)
                    }
                    setattr(item, key, value)

        if change_record["changes"]:
            item.customization_history.append(change_record)
            item.is_customized = True

        self.db.commit()
        self.db.refresh(item)
        return item

    def list_by_framework(
        self,
        framework: FrameworkEnum,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ChecklistItem]:
        """List checklist items by framework.

        Args:
            framework: Framework to filter by
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            List of checklist items
        """
        return self.db.query(ChecklistItem).filter(
            ChecklistItem.framework == framework
        ).offset(skip).limit(limit).all()

    def count_by_framework(self, framework: FrameworkEnum) -> int:
        """Count checklist items by framework.

        Args:
            framework: Framework to count

        Returns:
            Number of items
        """
        return self.db.query(ChecklistItem).filter(
            ChecklistItem.framework == framework
        ).count()


class ChecklistRepository:
    """Repository for checklist database operations."""

    def __init__(self, db: Session):
        """Initialize repository.

        Args:
            db: Database session
        """
        self.db = db

    def create(self, checklist: ChecklistCreate) -> Checklist:
        """Create a new checklist.

        Args:
            checklist: Checklist data

        Returns:
            Created checklist
        """
        db_checklist = Checklist(
            framework=checklist.framework,
            title=checklist.title,
            description=checklist.description,
            item_count=len(checklist.items),
        )

        self.db.add(db_checklist)
        self.db.commit()
        self.db.refresh(db_checklist)

        return db_checklist

    def get_by_id(self, checklist_id: UUID) -> Optional[Checklist]:
        """Get checklist by ID.

        Args:
            checklist_id: Checklist ID

        Returns:
            Checklist or None
        """
        return self.db.query(Checklist).filter(
            Checklist.id == checklist_id
        ).first()

    def get_latest_by_framework(self, framework: FrameworkEnum) -> Optional[Checklist]:
        """Get latest checklist for framework.

        Args:
            framework: Framework to filter by

        Returns:
            Latest checklist or None
        """
        return self.db.query(Checklist).filter(
            Checklist.framework == framework
        ).order_by(Checklist.version.desc()).first()

    def list_by_framework(
        self,
        framework: FrameworkEnum,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Checklist]:
        """List checklists by framework.

        Args:
            framework: Framework to filter by
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            List of checklists
        """
        return self.db.query(Checklist).filter(
            Checklist.framework == framework
        ).offset(skip).limit(limit).all()

    def increment_version(self, checklist_id: UUID) -> Optional[Checklist]:
        """Increment checklist version.

        Args:
            checklist_id: Checklist ID

        Returns:
            Updated checklist or None
        """
        checklist = self.get_by_id(checklist_id)
        if not checklist:
            return None

        checklist.version += 1
        self.db.commit()
        self.db.refresh(checklist)
        return checklist
