"""Compliance state database schema."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Text, DateTime, Index, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, ENUM

from rekon.db.schemas.base import BaseModel
from rekon.domain.models.compliance_state import ComplianceStatusEnum


class ComplianceState(BaseModel):
    """Compliance state database model."""

    __tablename__ = "compliance_states"

    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    checklist_item_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    status = Column(ENUM(ComplianceStatusEnum), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    evidence_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=False, default=[])
    last_assessed = Column(DateTime, nullable=False, default=datetime.utcnow)
    assessed_by = Column(UUID(as_uuid=True), nullable=False)

    __table_args__ = (
        Index("idx_organization_checklist", "organization_id", "checklist_item_id", unique=True),
        Index("idx_organization_status", "organization_id", "status"),
        Index("idx_last_assessed", "last_assessed"),
    )
