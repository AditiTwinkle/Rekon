"""Assessment repository for database operations."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from rekon.db.schemas.assessment import (
    GapAssessment,
    AssessmentQuestion,
    AssessmentResponse,
)
from rekon.domain.models.assessment import (
    GapAssessmentCreate,
    AssessmentStatusEnum,
)


class AssessmentRepository:
    """Repository for assessment operations."""

    def __init__(self, db: Session):
        """Initialize repository.

        Args:
            db: Database session
        """
        self.db = db

    def create_assessment(self, assessment: GapAssessmentCreate) -> GapAssessment:
        """Create a new gap assessment.

        Args:
            assessment: Assessment data to create

        Returns:
            Created assessment
        """
        db_assessment = GapAssessment(
            organization_id=assessment.organization_id,
            gap_id=assessment.gap_id,
            status=assessment.status,
        )
        self.db.add(db_assessment)
        self.db.commit()
        self.db.refresh(db_assessment)
        return db_assessment

    def get_assessment_by_id(self, assessment_id: UUID) -> Optional[GapAssessment]:
        """Get assessment by ID.

        Args:
            assessment_id: Assessment ID

        Returns:
            Assessment or None if not found
        """
        return self.db.query(GapAssessment).filter(
            GapAssessment.id == assessment_id
        ).first()

    def get_assessment_by_gap(self, gap_id: UUID) -> Optional[GapAssessment]:
        """Get assessment by gap ID.

        Args:
            gap_id: Gap ID

        Returns:
            Assessment or None if not found
        """
        return self.db.query(GapAssessment).filter(
            GapAssessment.gap_id == gap_id
        ).first()

    def list_by_organization(
        self,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[GapAssessment]:
        """List assessments by organization.

        Args:
            organization_id: Organization ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of assessments
        """
        return (
            self.db.query(GapAssessment)
            .filter(GapAssessment.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_assessment_status(
        self,
        assessment_id: UUID,
        status: AssessmentStatusEnum,
    ) -> Optional[GapAssessment]:
        """Update assessment status.

        Args:
            assessment_id: Assessment ID
            status: New status

        Returns:
            Updated assessment or None if not found
        """
        assessment = self.get_assessment_by_id(assessment_id)
        if not assessment:
            return None

        assessment.status = status
        self.db.commit()
        self.db.refresh(assessment)
        return assessment

    def add_question(
        self,
        assessment_id: UUID,
        question_number: int,
        question_text: str,
        regulatory_context: str,
        response_type: str,
        is_follow_up: bool = False,
        parent_question_id: Optional[UUID] = None,
    ) -> AssessmentQuestion:
        """Add a question to an assessment.

        Args:
            assessment_id: Assessment ID
            question_number: Question number
            question_text: Question text
            regulatory_context: Regulatory context
            response_type: Response type
            is_follow_up: Whether this is a follow-up question
            parent_question_id: Parent question ID if follow-up

        Returns:
            Created question
        """
        question = AssessmentQuestion(
            assessment_id=assessment_id,
            question_number=question_number,
            question_text=question_text,
            regulatory_context=regulatory_context,
            response_type=response_type,
            is_follow_up=1 if is_follow_up else 0,
            parent_question_id=parent_question_id,
        )
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def get_questions_by_assessment(
        self,
        assessment_id: UUID,
    ) -> List[AssessmentQuestion]:
        """Get all questions for an assessment.

        Args:
            assessment_id: Assessment ID

        Returns:
            List of questions
        """
        return self.db.query(AssessmentQuestion).filter(
            AssessmentQuestion.assessment_id == assessment_id
        ).order_by(AssessmentQuestion.question_number).all()

    def add_response(
        self,
        assessment_id: UUID,
        question_id: UUID,
        response_text: str,
        confidence_level: float,
        follow_up_question_ids: List[UUID] = None,
    ) -> AssessmentResponse:
        """Add a response to an assessment question.

        Args:
            assessment_id: Assessment ID
            question_id: Question ID
            response_text: Response text
            confidence_level: Confidence level (0-1)
            follow_up_question_ids: IDs of follow-up questions

        Returns:
            Created response
        """
        response = AssessmentResponse(
            assessment_id=assessment_id,
            question_id=question_id,
            response_text=response_text,
            confidence_level=confidence_level,
            follow_up_question_ids=follow_up_question_ids or [],
        )
        self.db.add(response)
        self.db.commit()
        self.db.refresh(response)
        return response

    def get_responses_by_assessment(
        self,
        assessment_id: UUID,
    ) -> List[AssessmentResponse]:
        """Get all responses for an assessment.

        Args:
            assessment_id: Assessment ID

        Returns:
            List of responses
        """
        return self.db.query(AssessmentResponse).filter(
            AssessmentResponse.assessment_id == assessment_id
        ).order_by(AssessmentResponse.response_timestamp).all()
