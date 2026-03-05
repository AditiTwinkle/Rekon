"""Assessment database schema."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Text, DateTime, Index, Float, Integer
from sqlalchemy.dialects.postgresql import UUID, ENUM, ARRAY

from rekon.db.schemas.base import BaseModel
from rekon.domain.models.assessment import (
    AssessmentStatusEnum,
    ResponseTypeEnum,
)


class GapAssessment(BaseModel):
    """Gap assessment database model."""

    __tablename__ = "gap_assessments"

    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    gap_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    status = Column(ENUM(AssessmentStatusEnum), nullable=False, default=AssessmentStatusEnum.IN_PROGRESS, index=True)
    assessment_started = Column(DateTime, nullable=False, default=datetime.utcnow)
    assessment_completed = Column(DateTime, nullable=True)
    questions_answered = Column(Integer, nullable=False, default=0)
    total_questions = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index("idx_organization_gap", "organization_id", "gap_id"),
        Index("idx_organization_status", "organization_id", "status"),
    )


class AssessmentQuestion(BaseModel):
    """Assessment question database model."""

    __tablename__ = "assessment_questions"

    assessment_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    regulatory_context = Column(Text, nullable=False)
    response_type = Column(ENUM(ResponseTypeEnum), nullable=False)
    is_follow_up = Column(Integer, nullable=False, default=0)
    parent_question_id = Column(UUID(as_uuid=True), nullable=True)

    __table_args__ = (
        Index("idx_assessment_questions", "assessment_id", "question_number"),
    )


class AssessmentResponse(BaseModel):
    """Assessment response database model."""

    __tablename__ = "assessment_responses"

    assessment_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    question_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    response_text = Column(Text, nullable=False)
    confidence_level = Column(Float, nullable=False)
    response_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    follow_up_question_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=False, default=[])

    __table_args__ = (
        Index("idx_assessment_responses", "assessment_id", "question_id"),
    )
