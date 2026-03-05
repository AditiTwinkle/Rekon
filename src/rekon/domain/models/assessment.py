"""Assessment domain models."""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class AssessmentStatusEnum(str, Enum):
    """Assessment status values."""

    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    PAUSED = "PAUSED"


class ResponseTypeEnum(str, Enum):
    """Response type values."""

    YES_NO = "YES_NO"
    FACTUAL = "FACTUAL"
    EVIDENCE = "EVIDENCE"


class QuestionBase(BaseModel):
    """Base question model."""

    question_text: str
    regulatory_context: str
    response_type: ResponseTypeEnum


class QuestionCreate(QuestionBase):
    """Model for creating questions."""

    assessment_id: UUID


class QuestionResponse(QuestionBase):
    """Model for question API responses."""

    question_id: UUID
    assessment_id: UUID
    question_number: int
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class AssessmentResponseBase(BaseModel):
    """Base assessment response model."""

    question_id: UUID
    response_text: str
    confidence_level: float = Field(ge=0, le=1)


class AssessmentResponseCreate(AssessmentResponseBase):
    """Model for creating assessment responses."""

    assessment_id: UUID


class AssessmentResponseModel(AssessmentResponseBase):
    """Model for assessment response API responses."""

    response_id: UUID
    assessment_id: UUID
    response_timestamp: datetime
    follow_up_questions: List[UUID] = Field(default_factory=list)

    class Config:
        """Pydantic config."""

        from_attributes = True


class GapAssessmentBase(BaseModel):
    """Base gap assessment model."""

    gap_id: UUID
    status: AssessmentStatusEnum


class GapAssessmentCreate(GapAssessmentBase):
    """Model for creating gap assessments."""

    organization_id: UUID


class GapAssessmentResponse(GapAssessmentBase):
    """Model for gap assessment API responses."""

    assessment_id: UUID
    organization_id: UUID
    assessment_started: datetime
    assessment_completed: Optional[datetime] = None
    questions_answered: int = 0
    total_questions: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class AssessmentSummaryResponse(BaseModel):
    """Model for assessment summary."""

    assessment_id: UUID
    gap_id: UUID
    status: AssessmentStatusEnum
    questions_answered: int
    identified_gaps: List[dict] = Field(default_factory=list)
    assessment_duration_minutes: int
    completion_percentage: float = Field(ge=0, le=100)
    next_steps: List[str] = Field(default_factory=list)
