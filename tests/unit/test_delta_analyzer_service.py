"""Unit tests for delta analyzer service."""

import pytest
from uuid import uuid4
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from rekon.db.schemas.base import BaseModel
from rekon.db.schemas.regulation import Regulation
from rekon.db.schemas.compliance_state import ComplianceState
from rekon.db.schemas.gap import ComplianceGap
from rekon.domain.models.regulation import FrameworkEnum
from rekon.domain.models.compliance_state import ComplianceStatusEnum
from rekon.domain.models.gap import GapTypeEnum, GapSeverityEnum
from rekon.services.delta_analyzer_service import DeltaAnalyzerService


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


def test_analyze_compliance_delta_no_gaps(db_session, organization_id, user_id):
    """Test delta analysis with no gaps."""
    # Create a regulation
    regulation = Regulation(
        framework=FrameworkEnum.DORA_A,
        requirement_number="5.1",
        title="Test Requirement",
        description="Test description",
        raw_content="Test content",
        source_url="https://example.com",
        content_hash="abc123",
    )
    db_session.add(regulation)
    db_session.commit()

    # Create compliant compliance state
    state = ComplianceState(
        organization_id=organization_id,
        checklist_item_id=regulation.id,
        status=ComplianceStatusEnum.COMPLIANT,
        assessed_by=user_id,
    )
    db_session.add(state)
    db_session.commit()

    # Perform analysis
    analyzer = DeltaAnalyzerService(db_session)
    result = analyzer.analyze_compliance_delta(organization_id, user_id)

    # Verify results
    assert result["organization_id"] == organization_id
    assert len(result["gaps_identified"]) == 0
    assert len(result["compliance_scores"]) > 0


def test_analyze_compliance_delta_identifies_non_compliant(
    db_session, organization_id, user_id
):
    """Test delta analysis identifies non-compliant gaps."""
    # Create a regulation
    regulation = Regulation(
        framework=FrameworkEnum.DORA_A,
        requirement_number="5.1",
        title="Test Requirement",
        description="Test description",
        raw_content="Test content",
        source_url="https://example.com",
        content_hash="abc123",
    )
    db_session.add(regulation)
    db_session.commit()

    # Create non-compliant compliance state
    state = ComplianceState(
        organization_id=organization_id,
        checklist_item_id=regulation.id,
        status=ComplianceStatusEnum.NON_COMPLIANT,
        assessed_by=user_id,
    )
    db_session.add(state)
    db_session.commit()

    # Perform analysis
    analyzer = DeltaAnalyzerService(db_session)
    result = analyzer.analyze_compliance_delta(organization_id, user_id)

    # Verify gaps were identified
    assert len(result["gaps_identified"]) == 1
    gap = result["gaps_identified"][0]
    assert gap.gap_type == GapTypeEnum.MISSING_CONTROL
    assert gap.severity == GapSeverityEnum.CRITICAL


def test_analyze_compliance_delta_identifies_partially_compliant(
    db_session, organization_id, user_id
):
    """Test delta analysis identifies partially compliant gaps."""
    # Create a regulation
    regulation = Regulation(
        framework=FrameworkEnum.SOX,
        requirement_number="302",
        title="Test Requirement",
        description="Test description",
        raw_content="Test content",
        source_url="https://example.com",
        content_hash="def456",
    )
    db_session.add(regulation)
    db_session.commit()

    # Create partially compliant compliance state
    state = ComplianceState(
        organization_id=organization_id,
        checklist_item_id=regulation.id,
        status=ComplianceStatusEnum.PARTIALLY_COMPLIANT,
        assessed_by=user_id,
    )
    db_session.add(state)
    db_session.commit()

    # Perform analysis
    analyzer = DeltaAnalyzerService(db_session)
    result = analyzer.analyze_compliance_delta(organization_id, user_id)

    # Verify gaps were identified
    assert len(result["gaps_identified"]) == 1
    gap = result["gaps_identified"][0]
    assert gap.gap_type == GapTypeEnum.INEFFECTIVE_CONTROL
    assert gap.severity == GapSeverityEnum.HIGH


def test_compliance_score_calculation(db_session, organization_id, user_id):
    """Test compliance score calculation."""
    # Create multiple regulations
    for i in range(3):
        regulation = Regulation(
            framework=FrameworkEnum.NIST,
            requirement_number=f"5.{i}",
            title=f"Test Requirement {i}",
            description="Test description",
            raw_content="Test content",
            source_url="https://example.com",
            content_hash=f"hash{i}",
        )
        db_session.add(regulation)
    db_session.commit()

    regulations = db_session.query(Regulation).all()

    # Create compliance states: 1 compliant, 1 partially, 1 non-compliant
    states = [
        ComplianceState(
            organization_id=organization_id,
            checklist_item_id=regulations[0].id,
            status=ComplianceStatusEnum.COMPLIANT,
            assessed_by=user_id,
        ),
        ComplianceState(
            organization_id=organization_id,
            checklist_item_id=regulations[1].id,
            status=ComplianceStatusEnum.PARTIALLY_COMPLIANT,
            assessed_by=user_id,
        ),
        ComplianceState(
            organization_id=organization_id,
            checklist_item_id=regulations[2].id,
            status=ComplianceStatusEnum.NON_COMPLIANT,
            assessed_by=user_id,
        ),
    ]
    for state in states:
        db_session.add(state)
    db_session.commit()

    # Perform analysis
    analyzer = DeltaAnalyzerService(db_session)
    result = analyzer.analyze_compliance_delta(organization_id, user_id)

    # Verify score calculation
    scores = result["compliance_scores"]
    nist_score = next((s for s in scores if s.framework == "NIST"), None)

    assert nist_score is not None
    assert nist_score.compliant_count == 1
    assert nist_score.partially_compliant_count == 1
    assert nist_score.non_compliant_count == 1
    # Score should be (1 + 0.5) / 3 * 100 = 50
    assert nist_score.score == 50.0


def test_gap_severity_classification(db_session, organization_id, user_id):
    """Test gap severity classification."""
    analyzer = DeltaAnalyzerService(db_session)

    # Test non-compliant missing control = CRITICAL
    severity = analyzer._classify_gap_severity(
        ComplianceStatusEnum.NON_COMPLIANT,
        GapTypeEnum.MISSING_CONTROL,
    )
    assert severity == GapSeverityEnum.CRITICAL

    # Test non-compliant ineffective control = HIGH
    severity = analyzer._classify_gap_severity(
        ComplianceStatusEnum.NON_COMPLIANT,
        GapTypeEnum.INEFFECTIVE_CONTROL,
    )
    assert severity == GapSeverityEnum.HIGH

    # Test partially compliant ineffective control = HIGH
    severity = analyzer._classify_gap_severity(
        ComplianceStatusEnum.PARTIALLY_COMPLIANT,
        GapTypeEnum.INEFFECTIVE_CONTROL,
    )
    assert severity == GapSeverityEnum.HIGH
