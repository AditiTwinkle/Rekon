"""Gap assessment service for interactive compliance assessments."""

import logging
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from rekon.db.repositories.assessment import AssessmentRepository
from rekon.db.repositories.gap import GapRepository
from rekon.domain.models.assessment import (
    GapAssessmentCreate,
    AssessmentStatusEnum,
    ResponseTypeEnum,
)

logger = logging.getLogger(__name__)


class GapAssessmentService:
    """Service for gap assessment operations."""

    def __init__(self, db: Session):
        """Initialize service.

        Args:
            db: Database session
        """
        self.db = db
        self.assessment_repository = AssessmentRepository(db)
        self.gap_repository = GapRepository(db)

    def start_assessment(
        self,
        organization_id: UUID,
        gap_id: UUID,
    ) -> Dict:
        """Start a new gap assessment.

        Args:
            organization_id: Organization ID
            gap_id: Gap ID

        Returns:
            Assessment with initial question
        """
        logger.info(f"Starting assessment for gap {gap_id}")

        # Create assessment
        assessment_create = GapAssessmentCreate(
            organization_id=organization_id,
            gap_id=gap_id,
            status=AssessmentStatusEnum.IN_PROGRESS,
        )
        assessment = self.assessment_repository.create_assessment(assessment_create)

        # Generate initial questions
        questions = self._generate_initial_questions(assessment.id, gap_id)

        logger.info(f"Assessment {assessment.id} started with {len(questions)} questions")

        return {
            "assessment_id": assessment.id,
            "gap_id": gap_id,
            "status": assessment.status,
            "questions": questions,
            "total_questions": len(questions),
        }

    def _generate_initial_questions(
        self,
        assessment_id: UUID,
        gap_id: UUID,
    ) -> List[Dict]:
        """Generate initial questions for assessment.

        Args:
            assessment_id: Assessment ID
            gap_id: Gap ID

        Returns:
            List of initial questions
        """
        # Get gap details
        gap = self.gap_repository.get_by_id(gap_id)
        if not gap:
            return []

        questions = []

        # Generate questions based on gap type
        if gap.gap_type.value == "MISSING_CONTROL":
            questions.extend(
                self._generate_missing_control_questions(assessment_id, gap)
            )
        elif gap.gap_type.value == "INEFFECTIVE_CONTROL":
            questions.extend(
                self._generate_ineffective_control_questions(assessment_id, gap)
            )
        elif gap.gap_type.value == "DOCUMENTATION_GAP":
            questions.extend(
                self._generate_documentation_gap_questions(assessment_id, gap)
            )

        return questions

    def _generate_missing_control_questions(
        self,
        assessment_id: UUID,
        gap,
    ) -> List[Dict]:
        """Generate questions for missing control gaps.

        Args:
            assessment_id: Assessment ID
            gap: Gap object

        Returns:
            List of questions
        """
        questions = []

        # Question 1: Is the control planned?
        q1 = self.assessment_repository.add_question(
            assessment_id=assessment_id,
            question_number=1,
            question_text="Is this control currently planned or in development?",
            regulatory_context=f"Gap: {gap.description}",
            response_type=ResponseTypeEnum.YES_NO,
        )
        questions.append(self._format_question(q1))

        # Question 2: Timeline for implementation
        q2 = self.assessment_repository.add_question(
            assessment_id=assessment_id,
            question_number=2,
            question_text="What is the planned timeline for implementing this control?",
            regulatory_context="Understanding implementation timeline helps prioritize remediation efforts",
            response_type=ResponseTypeEnum.FACTUAL,
        )
        questions.append(self._format_question(q2))

        # Question 3: Resource constraints
        q3 = self.assessment_repository.add_question(
            assessment_id=assessment_id,
            question_number=3,
            question_text="What are the main barriers to implementing this control?",
            regulatory_context="Identifying barriers helps develop realistic remediation plans",
            response_type=ResponseTypeEnum.FACTUAL,
        )
        questions.append(self._format_question(q3))

        return questions

    def _generate_ineffective_control_questions(
        self,
        assessment_id: UUID,
        gap,
    ) -> List[Dict]:
        """Generate questions for ineffective control gaps.

        Args:
            assessment_id: Assessment ID
            gap: Gap object

        Returns:
            List of questions
        """
        questions = []

        # Question 1: Root cause
        q1 = self.assessment_repository.add_question(
            assessment_id=assessment_id,
            question_number=1,
            question_text="What is the root cause of the control ineffectiveness?",
            regulatory_context=f"Gap: {gap.description}",
            response_type=ResponseTypeEnum.FACTUAL,
        )
        questions.append(self._format_question(q1))

        # Question 2: Testing frequency
        q2 = self.assessment_repository.add_question(
            assessment_id=assessment_id,
            question_number=2,
            question_text="How frequently is this control tested or validated?",
            regulatory_context="Testing frequency impacts control effectiveness assessment",
            response_type=ResponseTypeEnum.FACTUAL,
        )
        questions.append(self._format_question(q2))

        # Question 3: Remediation plan
        q3 = self.assessment_repository.add_question(
            assessment_id=assessment_id,
            question_number=3,
            question_text="Do you have a plan to remediate this control ineffectiveness?",
            regulatory_context="Understanding remediation plans helps prioritize actions",
            response_type=ResponseTypeEnum.YES_NO,
        )
        questions.append(self._format_question(q3))

        return questions

    def _generate_documentation_gap_questions(
        self,
        assessment_id: UUID,
        gap,
    ) -> List[Dict]:
        """Generate questions for documentation gaps.

        Args:
            assessment_id: Assessment ID
            gap: Gap object

        Returns:
            List of questions
        """
        questions = []

        # Question 1: Evidence availability
        q1 = self.assessment_repository.add_question(
            assessment_id=assessment_id,
            question_number=1,
            question_text="Do you have evidence that this control is implemented?",
            regulatory_context=f"Gap: {gap.description}",
            response_type=ResponseTypeEnum.YES_NO,
        )
        questions.append(self._format_question(q1))

        # Question 2: Evidence type
        q2 = self.assessment_repository.add_question(
            assessment_id=assessment_id,
            question_number=2,
            question_text="What type of evidence do you have (e.g., logs, reports, test results)?",
            regulatory_context="Understanding evidence type helps assess documentation completeness",
            response_type=ResponseTypeEnum.FACTUAL,
        )
        questions.append(self._format_question(q2))

        # Question 3: Evidence currency
        q3 = self.assessment_repository.add_question(
            assessment_id=assessment_id,
            question_number=3,
            question_text="When was this evidence last updated or generated?",
            regulatory_context="Evidence currency is critical for regulatory compliance",
            response_type=ResponseTypeEnum.FACTUAL,
        )
        questions.append(self._format_question(q3))

        return questions

    def _format_question(self, question) -> Dict:
        """Format question for response.

        Args:
            question: Question object

        Returns:
            Formatted question dictionary
        """
        return {
            "question_id": str(question.id),
            "question_number": question.question_number,
            "question_text": question.question_text,
            "regulatory_context": question.regulatory_context,
            "response_type": question.response_type.value,
        }

    def submit_response(
        self,
        assessment_id: UUID,
        question_id: UUID,
        response_text: str,
        confidence_level: float,
    ) -> Dict:
        """Submit a response to an assessment question.

        Args:
            assessment_id: Assessment ID
            question_id: Question ID
            response_text: Response text
            confidence_level: Confidence level (0-1)

        Returns:
            Response with next question or completion status
        """
        logger.info(f"Submitting response for assessment {assessment_id}")

        # Store response
        response = self.assessment_repository.add_response(
            assessment_id=assessment_id,
            question_id=question_id,
            response_text=response_text,
            confidence_level=confidence_level,
        )

        # Get assessment
        assessment = self.assessment_repository.get_assessment_by_id(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")

        # Update question count
        assessment.questions_answered += 1
        self.db.commit()

        # Get next question
        questions = self.assessment_repository.get_questions_by_assessment(
            assessment_id
        )
        next_question_number = assessment.questions_answered + 1

        if next_question_number <= len(questions):
            next_question = questions[next_question_number - 1]
            return {
                "response_id": str(response.id),
                "next_question": self._format_question(next_question),
                "progress": {
                    "answered": assessment.questions_answered,
                    "total": len(questions),
                    "percentage": (assessment.questions_answered / len(questions)) * 100,
                },
            }
        else:
            # Assessment complete
            assessment.status = AssessmentStatusEnum.COMPLETED
            assessment.assessment_completed = datetime.utcnow()
            self.db.commit()

            return {
                "response_id": str(response.id),
                "assessment_complete": True,
                "progress": {
                    "answered": assessment.questions_answered,
                    "total": len(questions),
                    "percentage": 100.0,
                },
            }

    def pause_assessment(self, assessment_id: UUID) -> Dict:
        """Pause an assessment.

        Args:
            assessment_id: Assessment ID

        Returns:
            Paused assessment details
        """
        assessment = self.assessment_repository.update_assessment_status(
            assessment_id,
            AssessmentStatusEnum.PAUSED,
        )

        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")

        return {
            "assessment_id": str(assessment.id),
            "status": assessment.status.value,
            "paused_at": datetime.utcnow().isoformat(),
        }

    def resume_assessment(self, assessment_id: UUID) -> Dict:
        """Resume a paused assessment.

        Args:
            assessment_id: Assessment ID

        Returns:
            Resumed assessment with next question
        """
        assessment = self.assessment_repository.get_assessment_by_id(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")

        # Update status
        assessment.status = AssessmentStatusEnum.IN_PROGRESS
        self.db.commit()

        # Get next question
        questions = self.assessment_repository.get_questions_by_assessment(
            assessment_id
        )
        next_question_number = assessment.questions_answered + 1

        if next_question_number <= len(questions):
            next_question = questions[next_question_number - 1]
            return {
                "assessment_id": str(assessment.id),
                "status": assessment.status.value,
                "next_question": self._format_question(next_question),
                "progress": {
                    "answered": assessment.questions_answered,
                    "total": len(questions),
                    "percentage": (assessment.questions_answered / len(questions)) * 100,
                },
            }
        else:
            return {
                "assessment_id": str(assessment.id),
                "status": AssessmentStatusEnum.COMPLETED.value,
                "assessment_complete": True,
            }

    def get_assessment_summary(self, assessment_id: UUID) -> Dict:
        """Get assessment summary.

        Args:
            assessment_id: Assessment ID

        Returns:
            Assessment summary
        """
        assessment = self.assessment_repository.get_assessment_by_id(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")

        questions = self.assessment_repository.get_questions_by_assessment(
            assessment_id
        )
        responses = self.assessment_repository.get_responses_by_assessment(
            assessment_id
        )

        duration = (
            (assessment.assessment_completed or datetime.utcnow())
            - assessment.assessment_started
        ).total_seconds() / 60

        return {
            "assessment_id": str(assessment.id),
            "gap_id": str(assessment.gap_id),
            "status": assessment.status.value,
            "questions_answered": assessment.questions_answered,
            "total_questions": len(questions),
            "completion_percentage": (
                (assessment.questions_answered / len(questions)) * 100
                if questions
                else 0
            ),
            "assessment_duration_minutes": int(duration),
            "responses": [
                {
                    "question_id": str(r.question_id),
                    "response_text": r.response_text,
                    "confidence_level": r.confidence_level,
                }
                for r in responses
            ],
        }
