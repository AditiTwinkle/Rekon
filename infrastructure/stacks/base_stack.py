"""Base CDK stack with common configuration."""

from aws_cdk import Stack
from constructs import Construct


class BaseStack(Stack):
    """Base stack for Rekon infrastructure."""

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        """Initialize base stack.

        Args:
            scope: CDK scope
            id: Stack ID
            **kwargs: Additional stack properties
        """
        super().__init__(scope, id, **kwargs)

        # Store context values
        self.environment = self.node.try_get_context("environment") or "dev"
        self.region = self.node.try_get_context("region") or "us-east-1"
        self.availability_zones = self.node.try_get_context("availability_zones") or [
            f"{self.region}a",
            f"{self.region}b",
        ]

        # Add tags
        self.tags.add("Environment", self.environment)
        self.tags.add("Project", "Rekon")
        self.tags.add("ManagedBy", "CDK")
