"""VPC stack for Rekon infrastructure."""

from aws_cdk import aws_ec2 as ec2
from constructs import Construct

from infrastructure.stacks.base_stack import BaseStack


class VpcStack(BaseStack):
    """VPC stack for Rekon infrastructure."""

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        """Initialize VPC stack.

        Args:
            scope: CDK scope
            id: Stack ID
            **kwargs: Additional stack properties
        """
        super().__init__(scope, id, **kwargs)

        # Create VPC
        self.vpc = ec2.Vpc(
            self,
            "RekonVpc",
            max_azs=2,
            nat_gateways=1,
            cidr="10.0.0.0/16",
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PUBLIC,
                    name="Public",
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    name="Private",
                    cidr_mask=24,
                ),
            ],
        )
