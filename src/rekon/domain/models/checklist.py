"""Checklist domain models."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from uuid import UUID

from pydantic import BaseModel, Field

from rekon.domain.models.regulation import FrameworkEnum


class PriorityEnum(str, Enum):
    """Priority levels for checklist items."""

    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class ChecklistItemBase(BaseModel):
    """Base checklist item model."""

    regulation_id: UUID
    framework: FrameworkEnum
    domain: str
    category: str
    requirement_text: str
    priority: PriorityEnum
    evidence_requirements: Dict
    regulatory_citation: str


class ChecklistItemCreate(ChecklistItemBase):
    """Model for creating checklist items."""

    pass


class ChecklistItemUpdate(BaseModel):
    """Model for updating checklist items."""

    requirement_text: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    evidence_requirements: Optional[Dict] = None
    domain: Optional[str] = None
    category: Optional[str] = None


class ChecklistItemResponse(ChecklistItemBase):
    """Model for checklist item API responses."""

    checklist_item_id: UUID
    version: int
    is_customized: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
        populate_by_name = True

    @classmethod
    def from_orm(cls, obj):
        """Convert ORM object to Pydantic model."""
        if obj is None:
            return None
        data = {
            "checklist_item_id": obj.id,
            "regulation_id": obj.regulation_id,
            "framework": obj.framework,
            "domain": obj.domain,
            "category": obj.category,
            "requirement_text": obj.requirement_text,
            "priority": obj.priority,
            "evidence_requirements": obj.evidence_requirements,
            "regulatory_citation": obj.regulatory_citation,
            "version": obj.version,
            "is_customized": obj.is_customized,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }
        return cls(**data)


class ChecklistBase(BaseModel):
    """Base checklist model."""

    framework: FrameworkEnum
    title: str
    description: Optional[str] = None


class ChecklistCreate(ChecklistBase):
    """Model for creating checklists."""

    items: List[ChecklistItemCreate] = []


class ChecklistResponse(ChecklistBase):
    """Model for checklist API responses."""

    checklist_id: UUID
    item_count: int
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
        populate_by_name = True

    @classmethod
    def from_orm(cls, obj):
        """Convert ORM object to Pydantic model."""
        if obj is None:
            return None
        data = {
            "checklist_id": obj.id,
            "framework": obj.framework,
            "title": obj.title,
            "description": obj.description,
            "item_count": obj.item_count,
            "version": obj.version,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }
        return cls(**data)
