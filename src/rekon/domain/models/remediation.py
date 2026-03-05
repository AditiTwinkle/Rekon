"""Remediation domain models."""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class RemediationStepStatusEnum(str, Enum):
    """Remediation step status values."""

    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"


class RemediationPriorityEnum(str, Enum):
    """Remediation priority values."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RemediationStepBase(BaseModel):
    """Base remediation step model."""

    step_number: int
    description: str
    priority: RemediationPriorityEnum
    estimated_effort_hours: int
    responsible_role: str
    success_criteria: str
    technical_guidance: Optional[str] = None
    process_template: Optional[str] = None


class RemediationStepCreate(RemediationStepBase):
    """Model for creating remediation steps."""

    remediation_id: UUID
    dependencies: List[int] = Field(default_factory=list)


class RemediationStepResponse(RemediationStepBase):
    """Model for remediation step API responses."""

    step_id: UUID
    remediation_id: UUID
    status: RemediationStepStatusEnum
    dependencies: List[int] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class RemediationPlanBase(BaseModel):
    """Base remediation plan model."""

    gap_id: UUID
    gap_summary: str
    root_cause: str
    total_estimated_effort_hours: int
    estimated_timeline_days: int


class RemediationPlanCreate(RemediationPlanBase):
    """Model for creating remediation plans."""

    organization_id: UUID


class RemediationPlanResponse(RemediationPlanBase):
    """Model for remediation plan API responses."""

    remediation_id: UUID
    organization_id: UUID
    steps: List[RemediationStepResponse] = Field(default_factory=list)
    resource_requirements: dict = Field(default_factory=dict)
    success_criteria: List[str] = Field(default_factory=list)
    risk_assessment: dict = Field(default_factory=dict)
    alternatives: List[dict] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class RemediationProgressResponse(BaseModel):
    """Model for remediation progress response."""

    remediation_id: UUID
    gap_id: UUID
    total_steps: int
    completed_steps: int
    in_progress_steps: int
    blocked_steps: int
    completion_percentage: float = Field(ge=0, le=100)
    estimated_completion_date: Optional[datetime] = None
    last_updated: datetime
