"""Gap database schema."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Text, DateTime, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ENUM

from rekon.db.schemas.base import BaseModel
from rekon.domain.models.gap import GapTypeEnum, GapSeverityEnum, GapStatusEnum


class ComplianceGap(BaseModel):
    """Compliance gap database model."""

    __tablename__ = "compliance_gaps"

    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    checklist_item_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    gap_type = Column(ENUM(GapTypeEnum), nullable=False, index=True)
    severity = Column(ENUM(GapSeverityEnum), nullable=False, index=True)
    description = Column(Text, nullable=False)
    root_cause = Column(Text, nullable=True)
    status = Column(ENUM(GapStatusEnum), nullable=False, default=GapStatusEnum.OPEN, index=True)
    identified_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    identified_by = Column(UUID(as_uuid=True), nullable=False)

    __table_args__ = (
        Index("idx_organization_status", "organization_id", "status"),
        Index("idx_organization_severity", "organization_id", "severity"),
        Index("idx_checklist_item_gaps", "checklist_item_id", "organization_id"),
    )
