"""EventBridge and Step Functions stack for event routing and orchestration."""

from aws_cdk import (
    aws_events as events,
    aws_events_targets as targets,
    aws_stepfunctions as sfn,
    Duration,
)
from constructs import Construct

from infrastructure.stacks.base_stack import BaseStack


class EventsStack(BaseStack):
    """EventBridge and Step Functions stack."""

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        """Initialize events stack.

        Args:
            scope: CDK scope
            id: Stack ID
            **kwargs: Additional stack properties
        """
        super().__init__(scope, id, **kwargs)

        # Create EventBridge rule for regulation updates
        self.regulation_update_rule = events.Rule(
            self,
            "RegulationUpdateRule",
            description="Route regulation update events",
            event_pattern=events.EventPattern(
                source=["rekon.regulations"],
                detail_type=["Regulation Updated"],
            ),
        )

        # Create EventBridge rule for checklist generation
        self.checklist_generation_rule = events.Rule(
            self,
            "ChecklistGenerationRule",
            description="Route checklist generation events",
            event_pattern=events.EventPattern(
                source=["rekon.checklists"],
                detail_type=["Checklist Generation Requested"],
            ),
        )

        # Create EventBridge rule for gap analysis
        self.gap_analysis_rule = events.Rule(
            self,
            "GapAnalysisRule",
            description="Route gap analysis events",
            event_pattern=events.EventPattern(
                source=["rekon.gaps"],
                detail_type=["Gap Analysis Requested"],
            ),
        )

        # Create EventBridge rule for scheduled regulation sync
        self.scheduled_sync_rule = events.Rule(
            self,
            "ScheduledSyncRule",
            description="Trigger scheduled regulation synchronization",
            schedule=events.Schedule.cron(hour="2", minute="0"),  # 2 AM UTC daily
        )

        # Create placeholder Step Functions state machine for compliance assessment
        self.compliance_assessment_sm = self._create_compliance_assessment_state_machine()

        # Create placeholder Step Functions state machine for regulation update
        self.regulation_update_sm = self._create_regulation_update_state_machine()

    def _create_compliance_assessment_state_machine(self) -> sfn.StateMachine:
        """Create compliance assessment state machine.

        Returns:
            State machine
        """
        # Placeholder state machine - will be expanded in later phases
        pass_state = sfn.Pass(self, "ComplianceAssessmentPass")

        return sfn.StateMachine(
            self,
            "ComplianceAssessmentSM",
            definition=pass_state,
            timeout=Duration.hours(1),
        )

    def _create_regulation_update_state_machine(self) -> sfn.StateMachine:
        """Create regulation update state machine.

        Returns:
            State machine
        """
        # Placeholder state machine - will be expanded in later phases
        pass_state = sfn.Pass(self, "RegulationUpdatePass")

        return sfn.StateMachine(
            self,
            "RegulationUpdateSM",
            definition=pass_state,
            timeout=Duration.hours(1),
        )
