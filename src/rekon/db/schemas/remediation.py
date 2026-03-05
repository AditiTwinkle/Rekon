"""Remediation database schema."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Text, DateTime, Index, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ENUM, ARRAY

from rekon.db.schemas.base import BaseModel
from rekon.domain.models.remediation import (
    RemediationStepStatusEnum,
    RemediationPriorityEnum,
)


class RemediationPlan(BaseModel):
    """Remediation plan database model."""

    __tablename__ = "remediation_plans"

    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    gap_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    gap_summary = Column(Text, nullable=False)
    root_cause = Column(Text, nullable=False)
    total_estimated_effort_hours = Column(Integer, nullable=False)
    estimated_timeline_days = Column(Integer, nullable=False)
    resource_requirements = Column(String(2000), nullable=True)
    success_criteria = Column(ARRAY(String), nullable=False, default=[])
    risk_assessment = Column(String(2000), nullable=True)
    alternatives = Column(String(2000), nullable=True)

    __table_args__ = (
        Index("idx_organization_gap", "organization_id", "gap_id"),
        Index("idx_gap_remediation", "gap_id"),
    )


class RemediationStep(BaseModel):
    """Remediation step database model."""

    __tablename__ = "remediation_steps"

    remediation_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    step_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(ENUM(RemediationPriorityEnum), nullable=False, index=True)
    estimated_effort_hours = Column(Integer, nullable=False)
    responsible_role = Column(String(255), nullable=False)
    success_criteria = Column(Text, nullable=False)
    technical_guidance = Column(Text, nullable=True)
    process_template = Column(Text, nullable=True)
    status = Column(
        ENUM(RemediationStepStatusEnum),
        nullable=False,
        default=RemediationStepStatusEnum.NOT_STARTED,
        index=True,
    )
    dependencies = Column(ARRAY(Integer), nullable=False, default=[])

    __table_args__ = (
        Index("idx_remediation_steps", "remediation_id", "step_number"),
        Index("idx_step_status", "remediation_id", "status"),
    )
