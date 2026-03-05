"""Unit tests for remediation service."""

import pytest
from uuid import uuid4
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from rekon.db.schemas.base import BaseModel
from rekon.db.schemas.gap import ComplianceGap
from rekon.domain.models.gap import GapTypeEnum, GapSeverityEnum
from rekon.domain.models.remediation import RemediationStepStatusEnum
from rekon.services.remediation_service import RemediationService


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


def test_generate_remediation_plan(db_session, organization_id, gap):
    """Test generating a remediation plan."""
    service = RemediationService(db_session)

    result = service.generate_remediation_plan(organization_id, gap.id)

    assert result["remediation_id"] is not None
    assert result["gap_id"] == gap.id
    assert len(result["steps"]) > 0
    assert result["total_estimated_effort_hours"] > 0
    assert result["estimated_timeline_days"] > 0


def test_generate_missing_control_steps(db_session, organization_id, gap):
    """Test that missing control gaps generate appropriate steps."""
    service = RemediationService(db_session)

    result = service.generate_remediation_plan(organization_id, gap.id)

    steps = result["steps"]
    assert len(steps) == 4

    # Verify step sequence
    assert steps[0]["step_number"] == 1
    assert "design" in steps[0]["description"].lower()

    assert steps[1]["step_number"] == 2
    assert "implement" in steps[1]["description"].lower()

    assert steps[2]["step_number"] == 3
    assert "test" in steps[2]["description"].lower()

    assert steps[3]["step_number"] == 4
    assert "evidence" in steps[3]["description"].lower()


def test_generate_ineffective_control_steps(db_session, organization_id, user_id):
    """Test that ineffective control gaps generate appropriate steps."""
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

    service = RemediationService(db_session)
    result = service.generate_remediation_plan(organization_id, gap.id)

    steps = result["steps"]
    assert len(steps) == 3

    # Verify step types
    assert "root cause" in steps[0]["description"].lower()
    assert "remediate" in steps[1]["description"].lower()
    assert "re-test" in steps[2]["description"].lower()


def test_generate_documentation_gap_steps(db_session, organization_id, user_id):
    """Test that documentation gaps generate appropriate steps."""
    # Create documentation gap
    gap = ComplianceGap(
        organization_id=organization_id,
        checklist_item_id=uuid4(),
        gap_type=GapTypeEnum.DOCUMENTATION_GAP,
        severity=GapSeverityEnum.MEDIUM,
        description="Test documentation gap",
        identified_by=user_id,
    )
    db_session.add(gap)
    db_session.commit()

    service = RemediationService(db_session)
    result = service.generate_remediation_plan(organization_id, gap.id)

    steps = result["steps"]
    assert len(steps) == 2

    # Verify step types
    assert "gather" in steps[0]["description"].lower()
    assert "document" in steps[1]["description"].lower()


def test_effort_estimation_by_severity(db_session, organization_id, user_id):
    """Test that effort estimation varies by gap severity."""
    service = RemediationService(db_session)

    # Create gaps with different severities
    severities = [
        (GapSeverityEnum.CRITICAL, 40),
        (GapSeverityEnum.HIGH, 24),
        (GapSeverityEnum.MEDIUM, 16),
        (GapSeverityEnum.LOW, 8),
    ]

    for severity, expected_effort in severities:
        gap = ComplianceGap(
            organization_id=organization_id,
            checklist_item_id=uuid4(),
            gap_type=GapTypeEnum.MISSING_CONTROL,
            severity=severity,
            description=f"Test {severity.value} gap",
            identified_by=user_id,
        )
        db_session.add(gap)
        db_session.commit()

        result = service.generate_remediation_plan(organization_id, gap.id)
        assert result["total_estimated_effort_hours"] == expected_effort


def test_update_step_status(db_session, organization_id, gap):
    """Test updating remediation step status."""
    service = RemediationService(db_session)

    # Generate plan
    result = service.generate_remediation_plan(organization_id, gap.id)
    step_id = result["steps"][0]["step_id"]

    # Update status
    updated_step = service.update_step_status(
        step_id,
        RemediationStepStatusEnum.IN_PROGRESS,
    )

    assert updated_step["status"] == RemediationStepStatusEnum.IN_PROGRESS.value


def test_get_remediation_progress(db_session, organization_id, gap):
    """Test getting remediation progress."""
    service = RemediationService(db_session)

    # Generate plan
    result = service.generate_remediation_plan(organization_id, gap.id)
    plan_id = result["remediation_id"]

    # Get progress
    progress = service.get_remediation_progress(plan_id)

    assert progress["remediation_id"] == str(plan_id)
    assert progress["gap_id"] == str(gap.id)
    assert progress["total_steps"] == len(result["steps"])
    assert progress["completed_steps"] == 0
    assert progress["completion_percentage"] == 0.0


def test_step_dependencies(db_session, organization_id, gap):
    """Test that remediation steps have correct dependencies."""
    service = RemediationService(db_session)

    result = service.generate_remediation_plan(organization_id, gap.id)
    steps = result["steps"]

    # For missing control, steps should have dependencies
    assert len(steps[0]["dependencies"]) == 0  # First step has no dependencies
    assert 1 in steps[1]["dependencies"]  # Second step depends on first
    assert 2 in steps[2]["dependencies"]  # Third step depends on second
    assert 3 in steps[3]["dependencies"]  # Fourth step depends on third
