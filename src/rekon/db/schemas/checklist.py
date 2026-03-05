"""Checklist database schemas."""

from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, Index, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSON

from rekon.db.schemas.base import BaseModel
from rekon.domain.models.regulation import FrameworkEnum
from rekon.domain.models.checklist import PriorityEnum


class ChecklistItem(BaseModel):
    """Checklist item database model."""

    __tablename__ = "checklist_items"

    regulation_id = Column(UUID, ForeignKey("regulations.id"), nullable=False)
    framework = Column(ENUM(FrameworkEnum), nullable=False, index=True)
    domain = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    requirement_text = Column(Text, nullable=False)
    priority = Column(ENUM(PriorityEnum), nullable=False)
    evidence_requirements = Column(JSON, nullable=False)
    regulatory_citation = Column(String(500), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    is_customized = Column(Boolean, nullable=False, default=False)
    customization_history = Column(JSON, nullable=True)

    __table_args__ = (
        Index("idx_framework_domain", "framework", "domain"),
        Index("idx_framework_priority", "framework", "priority"),
        Index("idx_regulation_id", "regulation_id"),
    )


class Checklist(BaseModel):
    """Checklist database model."""

    __tablename__ = "checklists"

    framework = Column(ENUM(FrameworkEnum), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    item_count = Column(Integer, nullable=False, default=0)
    version = Column(Integer, nullable=False, default=1)

    __table_args__ = (
        Index("idx_checklist_framework_version", "framework", "version"),
    )
