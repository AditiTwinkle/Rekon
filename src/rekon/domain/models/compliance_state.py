"""Compliance state domain models."""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class ComplianceStatusEnum(str, Enum):
    """Compliance status values."""

    COMPLIANT = "COMPLIANT"
    PARTIALLY_COMPLIANT = "PARTIALLY_COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ComplianceStateBase(BaseModel):
    """Base compliance state model."""

    checklist_item_id: UUID
    status: ComplianceStatusEnum
    notes: Optional[str] = None


class ComplianceStateCreate(ComplianceStateBase):
    """Model for creating compliance state."""

    organization_id: UUID
    assessed_by: UUID


class ComplianceStateUpdate(BaseModel):
    """Model for updating compliance state."""

    status: Optional[ComplianceStatusEnum] = None
    notes: Optional[str] = None


class ComplianceStateResponse(ComplianceStateBase):
    """Model for compliance state API responses."""

    compliance_state_id: UUID
    organization_id: UUID
    evidence_ids: List[UUID] = Field(default_factory=list)
    last_assessed: datetime
    assessed_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class ComplianceScoreResponse(BaseModel):
    """Model for compliance score response."""

    framework: str
    score: float = Field(ge=0, le=100)
    compliant_count: int
    partially_compliant_count: int
    non_compliant_count: int
    not_applicable_count: int
    total_applicable: int
    calculated_at: datetime
