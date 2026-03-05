"""Remediation repository for database operations."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from rekon.db.schemas.remediation import RemediationPlan, RemediationStep
from rekon.domain.models.remediation import (
    RemediationPlanCreate,
    RemediationStepCreate,
    RemediationStepStatusEnum,
)


class RemediationRepository:
    """Repository for remediation operations."""

    def __init__(self, db: Session):
        """Initialize repository.

        Args:
            db: Database session
        """
        self.db = db

    def create_plan(self, plan: RemediationPlanCreate) -> RemediationPlan:
        """Create a new remediation plan.

        Args:
            plan: Remediation plan data to create

        Returns:
            Created remediation plan
        """
        db_plan = RemediationPlan(
            organization_id=plan.organization_id,
            gap_id=plan.gap_id,
            gap_summary=plan.gap_summary,
            root_cause=plan.root_cause,
            total_estimated_effort_hours=plan.total_estimated_effort_hours,
            estimated_timeline_days=plan.estimated_timeline_days,
        )
        self.db.add(db_plan)
        self.db.commit()
        self.db.refresh(db_plan)
        return db_plan

    def get_plan_by_id(self, plan_id: UUID) -> Optional[RemediationPlan]:
        """Get remediation plan by ID.

        Args:
            plan_id: Plan ID

        Returns:
            Remediation plan or None if not found
        """
        return self.db.query(RemediationPlan).filter(
            RemediationPlan.id == plan_id
        ).first()

    def get_plan_by_gap(self, gap_id: UUID) -> Optional[RemediationPlan]:
        """Get remediation plan by gap ID.

        Args:
            gap_id: Gap ID

        Returns:
            Remediation plan or None if not found
        """
        return self.db.query(RemediationPlan).filter(
            RemediationPlan.gap_id == gap_id
        ).first()

    def list_by_organization(
        self,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[RemediationPlan]:
        """List remediation plans by organization.

        Args:
            organization_id: Organization ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of remediation plans
        """
        return (
            self.db.query(RemediationPlan)
            .filter(RemediationPlan.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def add_step(self, step: RemediationStepCreate) -> RemediationStep:
        """Add a remediation step.

        Args:
            step: Remediation step data to create

        Returns:
            Created remediation step
        """
        db_step = RemediationStep(
            remediation_id=step.remediation_id,
            step_number=step.step_number,
            description=step.description,
            priority=step.priority,
            estimated_effort_hours=step.estimated_effort_hours,
            responsible_role=step.responsible_role,
            success_criteria=step.success_criteria,
            technical_guidance=step.technical_guidance,
            process_template=step.process_template,
            dependencies=step.dependencies,
        )
        self.db.add(db_step)
        self.db.commit()
        self.db.refresh(db_step)
        return db_step

    def get_steps_by_plan(self, plan_id: UUID) -> List[RemediationStep]:
        """Get all steps for a remediation plan.

        Args:
            plan_id: Plan ID

        Returns:
            List of remediation steps
        """
        return (
            self.db.query(RemediationStep)
            .filter(RemediationStep.remediation_id == plan_id)
            .order_by(RemediationStep.step_number)
            .all()
        )

    def update_step_status(
        self,
        step_id: UUID,
        status: RemediationStepStatusEnum,
    ) -> Optional[RemediationStep]:
        """Update remediation step status.

        Args:
            step_id: Step ID
            status: New status

        Returns:
            Updated step or None if not found
        """
        step = self.db.query(RemediationStep).filter(
            RemediationStep.id == step_id
        ).first()

        if not step:
            return None

        step.status = status
        self.db.commit()
        self.db.refresh(step)
        return step

    def get_step_progress(self, plan_id: UUID) -> dict:
        """Get progress summary for a remediation plan.

        Args:
            plan_id: Plan ID

        Returns:
            Progress summary with step counts
        """
        steps = self.get_steps_by_plan(plan_id)

        if not steps:
            return {
                "total_steps": 0,
                "completed_steps": 0,
                "in_progress_steps": 0,
                "blocked_steps": 0,
                "not_started_steps": 0,
                "completion_percentage": 0.0,
            }

        completed = sum(
            1 for s in steps if s.status == RemediationStepStatusEnum.COMPLETED
        )
        in_progress = sum(
            1 for s in steps if s.status == RemediationStepStatusEnum.IN_PROGRESS
        )
        blocked = sum(
            1 for s in steps if s.status == RemediationStepStatusEnum.BLOCKED
        )
        not_started = sum(
            1 for s in steps if s.status == RemediationStepStatusEnum.NOT_STARTED
        )

        return {
            "total_steps": len(steps),
            "completed_steps": completed,
            "in_progress_steps": in_progress,
            "blocked_steps": blocked,
            "not_started_steps": not_started,
            "completion_percentage": (completed / len(steps)) * 100 if steps else 0,
        }
