"""Gap domain models."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class GapTypeEnum(str, Enum):
    """Types of compliance gaps."""

    MISSING_CONTROL = "MISSING_CONTROL"
    INEFFECTIVE_CONTROL = "INEFFECTIVE_CONTROL"
    DOCUMENTATION_GAP = "DOCUMENTATION_GAP"


class GapSeverityEnum(str, Enum):
    """Gap severity levels."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class GapStatusEnum(str, Enum):
    """Gap status values."""

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"


class ComplianceGapBase(BaseModel):
    """Base gap model."""

    checklist_item_id: UUID
    gap_type: GapTypeEnum
    severity: GapSeverityEnum
    description: str
    root_cause: Optional[str] = None


class ComplianceGapCreate(ComplianceGapBase):
    """Model for creating gaps."""

    organization_id: UUID
    identified_by: UUID


class ComplianceGapUpdate(BaseModel):
    """Model for updating gaps."""

    status: Optional[GapStatusEnum] = None
    root_cause: Optional[str] = None
    description: Optional[str] = None


class ComplianceGapResponse(ComplianceGapBase):
    """Model for gap API responses."""

    gap_id: UUID
    organization_id: UUID
    status: GapStatusEnum
    identified_at: datetime
    identified_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
