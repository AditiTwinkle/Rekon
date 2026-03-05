"""Unit tests for gap assessment service."""

import pytest
from uuid import uuid4
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from rekon.db.schemas.base import BaseModel
from rekon.db.schemas.gap import ComplianceGap
from rekon.db.schemas.assessment import GapAssessment
from rekon.domain.models.gap import GapTypeEnum, GapSeverityEnum, GapStatusEnum
from rekon.domain.models.assessment import AssessmentStatusEnum, ResponseTypeEnum
from rekon.services.gap_assessment_service import GapAssessmentService


@pytest.fixture
def db_session():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    BaseModel.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def organization_id():
    """Generate organization ID."""
    return uuid4()


@pytest.fixture
def user_id():
    """Generate user ID."""
    return uuid4()


@pytest.fixture
def gap(db_session, organization_id, user_id):
    """Create a test gap."""
    gap = ComplianceGap(
        organization_id=organization_id,
        checklist_item_id=uuid4(),
        gap_type=GapTypeEnum.MISSING_CONTROL,
        severity=GapSeverityEnum.CRITICAL,
        description="Test missing control gap",
        identified_by=user_id,
    )
    db_session.add(gap)
    db_session.commit()
    return gap


def test_start_assessment(db_session, organization_id, gap):
    """Test starting a new assessment."""
    service = GapAssessmentService(db_session)

    result = service.start_assessment(organization_id, gap.id)

    assert result["assessment_id"] is not None
    assert result["gap_id"] == gap.id
    assert result["status"] == AssessmentStatusEnum.IN_PROGRESS
    assert len(result["questions"]) > 0
    assert result["total_questions"] > 0


def test_start_assessment_missing_control_questions(db_session, organization_id, gap):
    """Test that missing control gaps generate appropriate questions."""
    service = GapAssessmentService(db_session)

    result = service.start_assessment(organization_id, gap.id)

    questions = result["questions"]
    assert len(questions) == 3

    # Verify question types
    assert questions[0]["question_text"] == "Is this control currently planned or in development?"
    assert questions[0]["response_type"] == ResponseTypeEnum.YES_NO.value

    assert questions[1]["question_text"] == "What is the planned timeline for implementing this control?"
    assert questions[1]["response_type"] == ResponseTypeEnum.FACTUAL.value

    assert questions[2]["question_text"] == "What are the main barriers to implementing this control?"
    assert questions[2]["response_type"] == ResponseTypeEnum.FACTUAL.value


def test_start_assessment_ineffective_control_questions(
    db_session, organization_id, user_id
):
    """Test that ineffective control gaps generate appropriate questions."""
    # Create ineffective control gap
    gap = ComplianceGap(
        organization_id=organization_id,
        checklist_item_id=uuid4(),
        gap_type=GapTypeEnum.INEFFECTIVE_CONTROL,
        severity=GapSeverityEnum.HIGH,
        description="Test ineffective control gap",
        identified_by=user_id,
    )
    db_session.add(gap)
    db_session.commit()

    service = GapAssessmentService(db_session)
    result = service.start_assessment(organization_id, gap.id)

    questions = result["questions"]
    assert len(questions) == 3

    # Verify question types
    assert "root cause" in questions[0]["question_text"].lower()
    assert "testing" in questions[1]["question_text"].lower()
    assert "remediation" in questions[2]["question_text"].lower()


def test_submit_response(db_session, organization_id, gap):
    """Test submitting a response to an assessment question."""
    service = GapAssessmentService(db_session)

    # Start assessment
    assessment_result = service.start_assessment(organization_id, gap.id)
    assessment_id = assessment_result["assessment_id"]
    question_id = assessment_result["questions"][0]["question_id"]

    # Submit response
    response_result = service.submit_response(
        assessment_id,
        question_id,
        "Yes, the control is planned",
        0.9,
    )

    assert response_result["response_id"] is not None
    assert "next_question" in response_result
    assert response_result["progress"]["answered"] == 1
    assert response_result["progress"]["percentage"] > 0


def test_assessment_completion(db_session, organization_id, gap):
    """Test completing an assessment."""
    service = GapAssessmentService(db_session)

    # Start assessment
    assessment_result = service.start_assessment(organization_id, gap.id)
    assessment_id = assessment_result["assessment_id"]
    questions = assessment_result["questions"]

    # Submit responses for all questions
    for i, question in enumerate(questions):
        response_result = service.submit_response(
            assessment_id,
            question["question_id"],
            f"Response to question {i+1}",
            0.8,
        )

        if i == len(questions) - 1:
            # Last question should complete assessment
            assert response_result["assessment_complete"] is True
            assert response_result["progress"]["percentage"] == 100.0
        else:
            assert "next_question" in response_result


def test_pause_and_resume_assessment(db_session, organization_id, gap):
    """Test pausing and resuming an assessment."""
    service = GapAssessmentService(db_session)

    # Start assessment
    assessment_result = service.start_assessment(organization_id, gap.id)
    assessment_id = assessment_result["assessment_id"]
    question_id = assessment_result["questions"][0]["question_id"]

    # Submit one response
    service.submit_response(
        assessment_id,
        question_id,
        "Response to first question",
        0.8,
    )

    # Pause assessment
    pause_result = service.pause_assessment(assessment_id)
    assert pause_result["status"] == AssessmentStatusEnum.PAUSED.value

    # Resume assessment
    resume_result = service.resume_assessment(assessment_id)
    assert resume_result["status"] == AssessmentStatusEnum.IN_PROGRESS.value
    assert "next_question" in resume_result
    assert resume_result["progress"]["answered"] == 1


def test_get_assessment_summary(db_session, organization_id, gap):
    """Test getting assessment summary."""
    service = GapAssessmentService(db_session)

    # Start assessment
    assessment_result = service.start_assessment(organization_id, gap.id)
    assessment_id = assessment_result["assessment_id"]
    questions = assessment_result["questions"]

    # Submit responses for all questions
    for i, question in enumerate(questions):
        service.submit_response(
            assessment_id,
            question["question_id"],
            f"Response to question {i+1}",
            0.8,
        )

    # Get summary
    summary = service.get_assessment_summary(assessment_id)

    assert summary["assessment_id"] == str(assessment_id)
    assert summary["gap_id"] == str(gap.id)
    assert summary["status"] == AssessmentStatusEnum.COMPLETED.value
    assert summary["questions_answered"] == len(questions)
    assert summary["total_questions"] == len(questions)
    assert summary["completion_percentage"] == 100.0
    assert len(summary["responses"]) == len(questions)
