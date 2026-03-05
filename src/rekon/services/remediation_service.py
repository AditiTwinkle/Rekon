"""Remediation service for remediation plan management."""

import logging
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from rekon.db.repositories.remediation import RemediationRepository
from rekon.db.repositories.gap import GapRepository
from rekon.domain.models.remediation import (
    RemediationPlanCreate,
    RemediationStepCreate,
    RemediationStepStatusEnum,
    RemediationPriorityEnum,
)

logger = logging.getLogger(__name__)


class RemediationService:
    """Service for remediation operations."""

    def __init__(self, db: Session):
        """Initialize service.

        Args:
            db: Database session
        """
        self.db = db
        self.remediation_repository = RemediationRepository(db)
        self.gap_repository = GapRepository(db)

    def generate_remediation_plan(
        self,
        organization_id: UUID,
        gap_id: UUID,
    ) -> Dict:
        """Generate a remediation plan for a gap.

        Args:
            organization_id: Organization ID
            gap_id: Gap ID

        Returns:
            Generated remediation plan
        """
        logger.info(f"Generating remediation plan for gap {gap_id}")

        # Get gap details
        gap = self.gap_repository.get_by_id(gap_id)
        if not gap:
            raise ValueError(f"Gap {gap_id} not found")

        # Create remediation plan
        plan_create = RemediationPlanCreate(
            organization_id=organization_id,
            gap_id=gap_id,
            gap_summary=gap.description,
            root_cause=gap.root_cause or "Root cause to be determined",
            total_estimated_effort_hours=self._estimate_effort(gap),
            estimated_timeline_days=self._estimate_timeline(gap),
        )

        plan = self.remediation_repository.create_plan(plan_create)

        # Generate remediation steps
        steps = self._generate_remediation_steps(plan.id, gap)

        logger.info(f"Remediation plan {plan.id} generated with {len(steps)} steps")

        return {
            "remediation_id": plan.id,
            "gap_id": gap_id,
            "gap_summary": plan.gap_summary,
            "root_cause": plan.root_cause,
            "steps": steps,
            "total_estimated_effort_hours": plan.total_estimated_effort_hours,
            "estimated_timeline_days": plan.estimated_timeline_days,
        }

    def _estimate_effort(self, gap) -> int:
        """Estimate effort for remediation based on gap severity.

        Args:
            gap: Gap object

        Returns:
            Estimated effort in hours
        """
        severity_effort_map = {
            "CRITICAL": 40,
            "HIGH": 24,
            "MEDIUM": 16,
            "LOW": 8,
        }
        return severity_effort_map.get(gap.severity.value, 16)

    def _estimate_timeline(self, gap) -> int:
        """Estimate timeline for remediation based on gap severity.

        Args:
            gap: Gap object

        Returns:
            Estimated timeline in days
        """
        severity_timeline_map = {
            "CRITICAL": 5,
            "HIGH": 10,
            "MEDIUM": 15,
            "LOW": 30,
        }
        return severity_timeline_map.get(gap.severity.value, 15)

    def _generate_remediation_steps(
        self,
        plan_id: UUID,
        gap,
    ) -> List[Dict]:
        """Generate remediation steps for a gap.

        Args:
            plan_id: Remediation plan ID
            gap: Gap object

        Returns:
            List of remediation steps
        """
        steps = []

        if gap.gap_type.value == "MISSING_CONTROL":
            steps = self._generate_missing_control_steps(plan_id, gap)
        elif gap.gap_type.value == "INEFFECTIVE_CONTROL":
            steps = self._generate_ineffective_control_steps(plan_id, gap)
        elif gap.gap_type.value == "DOCUMENTATION_GAP":
            steps = self._generate_documentation_gap_steps(plan_id, gap)

        return steps

    def _generate_missing_control_steps(
        self,
        plan_id: UUID,
        gap,
    ) -> List[Dict]:
        """Generate steps for missing control gaps.

        Args:
            plan_id: Remediation plan ID
            gap: Gap object

        Returns:
            List of remediation steps
        """
        steps = []

        # Step 1: Design the control
        step1 = RemediationStepCreate(
            remediation_id=plan_id,
            step_number=1,
            description="Design the control to address the compliance requirement",
            priority=RemediationPriorityEnum.CRITICAL,
            estimated_effort_hours=8,
            responsible_role="Compliance Officer",
            success_criteria="Control design document approved by management",
            technical_guidance="Document control objectives, procedures, and responsibilities",
            dependencies=[],
        )
        created_step1 = self.remediation_repository.add_step(step1)
        steps.append(self._format_step(created_step1))

        # Step 2: Implement the control
        step2 = RemediationStepCreate(
            remediation_id=plan_id,
            step_number=2,
            description="Implement the control in the organization",
            priority=RemediationPriorityEnum.CRITICAL,
            estimated_effort_hours=16,
            responsible_role="IT Manager",
            success_criteria="Control is operational and documented",
            technical_guidance="Follow control design document for implementation",
            dependencies=[1],
        )
        created_step2 = self.remediation_repository.add_step(step2)
        steps.append(self._format_step(created_step2))

        # Step 3: Test the control
        step3 = RemediationStepCreate(
            remediation_id=plan_id,
            step_number=3,
            description="Test the control to verify effectiveness",
            priority=RemediationPriorityEnum.HIGH,
            estimated_effort_hours=8,
            responsible_role="QA Manager",
            success_criteria="Control testing completed with satisfactory results",
            technical_guidance="Execute test procedures and document results",
            dependencies=[2],
        )
        created_step3 = self.remediation_repository.add_step(step3)
        steps.append(self._format_step(created_step3))

        # Step 4: Document evidence
        step4 = RemediationStepCreate(
            remediation_id=plan_id,
            step_number=4,
            description="Collect and document evidence of control implementation",
            priority=RemediationPriorityEnum.HIGH,
            estimated_effort_hours=4,
            responsible_role="Compliance Officer",
            success_criteria="Evidence package prepared and stored",
            technical_guidance="Collect test results, logs, and configuration documentation",
            dependencies=[3],
        )
        created_step4 = self.remediation_repository.add_step(step4)
        steps.append(self._format_step(created_step4))

        return steps

    def _generate_ineffective_control_steps(
        self,
        plan_id: UUID,
        gap,
    ) -> List[Dict]:
        """Generate steps for ineffective control gaps.

        Args:
            plan_id: Remediation plan ID
            gap: Gap object

        Returns:
            List of remediation steps
        """
        steps = []

        # Step 1: Root cause analysis
        step1 = RemediationStepCreate(
            remediation_id=plan_id,
            step_number=1,
            description="Conduct root cause analysis of control ineffectiveness",
            priority=RemediationPriorityEnum.HIGH,
            estimated_effort_hours=8,
            responsible_role="Compliance Officer",
            success_criteria="Root cause analysis completed and documented",
            technical_guidance="Interview stakeholders and review control execution logs",
            dependencies=[],
        )
        created_step1 = self.remediation_repository.add_step(step1)
        steps.append(self._format_step(created_step1))

        # Step 2: Remediate root cause
        step2 = RemediationStepCreate(
            remediation_id=plan_id,
            step_number=2,
            description="Implement remediation for identified root cause",
            priority=RemediationPriorityEnum.HIGH,
            estimated_effort_hours=12,
            responsible_role="IT Manager",
            success_criteria="Root cause remediation completed and verified",
            technical_guidance="Follow remediation plan from root cause analysis",
            dependencies=[1],
        )
        created_step2 = self.remediation_repository.add_step(step2)
        steps.append(self._format_step(created_step2))

        # Step 3: Re-test control
        step3 = RemediationStepCreate(
            remediation_id=plan_id,
            step_number=3,
            description="Re-test control to verify effectiveness",
            priority=RemediationPriorityEnum.HIGH,
            estimated_effort_hours=8,
            responsible_role="QA Manager",
            success_criteria="Control re-testing completed with satisfactory results",
            technical_guidance="Execute control test procedures and document results",
            dependencies=[2],
        )
        created_step3 = self.remediation_repository.add_step(step3)
        steps.append(self._format_step(created_step3))

        return steps

    def _generate_documentation_gap_steps(
        self,
        plan_id: UUID,
        gap,
    ) -> List[Dict]:
        """Generate steps for documentation gaps.

        Args:
            plan_id: Remediation plan ID
            gap: Gap object

        Returns:
            List of remediation steps
        """
        steps = []

        # Step 1: Gather evidence
        step1 = RemediationStepCreate(
            remediation_id=plan_id,
            step_number=1,
            description="Gather existing evidence of control implementation",
            priority=RemediationPriorityEnum.MEDIUM,
            estimated_effort_hours=4,
            responsible_role="Compliance Officer",
            success_criteria="All available evidence collected and organized",
            technical_guidance="Search systems for logs, reports, and configuration files",
            dependencies=[],
        )
        created_step1 = self.remediation_repository.add_step(step1)
        steps.append(self._format_step(created_step1))

        # Step 2: Document evidence
        step2 = RemediationStepCreate(
            remediation_id=plan_id,
            step_number=2,
            description="Document and organize evidence for regulatory review",
            priority=RemediationPriorityEnum.MEDIUM,
            estimated_effort_hours=6,
            responsible_role="Compliance Officer",
            success_criteria="Evidence package prepared with proper documentation",
            technical_guidance="Create evidence index and store in compliance repository",
            dependencies=[1],
        )
        created_step2 = self.remediation_repository.add_step(step2)
        steps.append(self._format_step(created_step2))

        return steps

    def _format_step(self, step) -> Dict:
        """Format remediation step for response.

        Args:
            step: Remediation step object

        Returns:
            Formatted step dictionary
        """
        return {
            "step_id": str(step.id),
            "step_number": step.step_number,
            "description": step.description,
            "priority": step.priority.value,
            "estimated_effort_hours": step.estimated_effort_hours,
            "responsible_role": step.responsible_role,
            "success_criteria": step.success_criteria,
            "technical_guidance": step.technical_guidance,
            "process_template": step.process_template,
            "status": step.status.value,
            "dependencies": step.dependencies,
        }

    def update_step_status(
        self,
        step_id: UUID,
        status: RemediationStepStatusEnum,
    ) -> Dict:
        """Update remediation step status.

        Args:
            step_id: Step ID
            status: New status

        Returns:
            Updated step
        """
        step = self.remediation_repository.update_step_status(step_id, status)
        if not step:
            raise ValueError(f"Step {step_id} not found")

        return self._format_step(step)

    def get_remediation_progress(self, plan_id: UUID) -> Dict:
        """Get remediation plan progress.

        Args:
            plan_id: Plan ID

        Returns:
            Progress summary
        """
        plan = self.remediation_repository.get_plan_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")

        progress = self.remediation_repository.get_step_progress(plan_id)

        return {
            "remediation_id": str(plan_id),
            "gap_id": str(plan.gap_id),
            **progress,
            "estimated_completion_date": (
                datetime.utcnow() + timedelta(days=plan.estimated_timeline_days)
            ).isoformat(),
        }
