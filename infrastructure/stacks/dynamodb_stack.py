"""DynamoDB stack for session and state management."""

from aws_cdk import (
    aws_dynamodb as dynamodb,
    RemovalPolicy,
    Duration,
)
from constructs import Construct

from infrastructure.stacks.base_stack import BaseStack


class DynamoDBStack(BaseStack):
    """DynamoDB stack for session and state management."""

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        """Initialize DynamoDB stack.

        Args:
            scope: CDK scope
            id: Stack ID
            **kwargs: Additional stack properties
        """
        super().__init__(scope, id, **kwargs)

        # Create table for assessment sessions
        self.sessions_table = dynamodb.Table(
            self,
            "SessionsTable",
            table_name="rekon-sessions",
            partition_key=dynamodb.Attribute(
                name="session_id",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            time_to_live_attribute="ttl",
            point_in_time_recovery=True,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
        )

        # Add GSI for organization_id
        self.sessions_table.add_global_secondary_index(
            index_name="organization_id-index",
            partition_key=dynamodb.Attribute(
                name="organization_id",
                type=dynamodb.AttributeType.STRING,
            ),
            projection=dynamodb.ProjectionType.ALL,
        )

        # Create table for compliance state
        self.compliance_state_table = dynamodb.Table(
            self,
            "ComplianceStateTable",
            table_name="rekon-compliance-state",
            partition_key=dynamodb.Attribute(
                name="organization_id",
                type=dynamodb.AttributeType.STRING,
            ),
            sort_key=dynamodb.Attribute(
                name="checklist_item_id",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery=True,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
        )

        # Create table for gap assessments
        self.assessments_table = dynamodb.Table(
            self,
            "AssessmentsTable",
            table_name="rekon-assessments",
            partition_key=dynamodb.Attribute(
                name="assessment_id",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            time_to_live_attribute="ttl",
            point_in_time_recovery=True,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
        )

        # Add GSI for organization_id
        self.assessments_table.add_global_secondary_index(
            index_name="organization_id-index",
            partition_key=dynamodb.Attribute(
                name="organization_id",
                type=dynamodb.AttributeType.STRING,
            ),
            projection=dynamodb.ProjectionType.ALL,
        )
