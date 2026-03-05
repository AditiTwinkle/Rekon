"""S3 storage stack for evidence and reports."""

from aws_cdk import (
    aws_s3 as s3,
    aws_kms as kms,
    RemovalPolicy,
    Duration,
)
from constructs import Construct

from infrastructure.stacks.base_stack import BaseStack


class StorageStack(BaseStack):
    """S3 storage stack for evidence and reports."""

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        """Initialize storage stack.

        Args:
            scope: CDK scope
            id: Stack ID
            **kwargs: Additional stack properties
        """
        super().__init__(scope, id, **kwargs)

        # Create KMS key for encryption
        self.kms_key = kms.Key(
            self,
            "EvidenceKey",
            enable_key_rotation=True,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # Create S3 bucket for evidence storage
        self.evidence_bucket = s3.Bucket(
            self,
            "EvidenceBucket",
            bucket_name=f"rekon-evidence-{self.account}-{self.region}",
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.kms_key,
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            removal_policy=RemovalPolicy.RETAIN,
            lifecycle_rules=[
                s3.LifecycleRule(
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INTELLIGENT_TIERING,
                            transition_after=Duration.days(30),
                        ),
                        s3.Transition(
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=Duration.days(90),
                        ),
                    ],
                    noncurrent_version_transitions=[
                        s3.NoncurrentVersionTransition(
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=Duration.days(30),
                        ),
                    ],
                    noncurrent_version_expiration=Duration.days(365),
                ),
            ],
        )

        # Create S3 bucket for reports
        self.reports_bucket = s3.Bucket(
            self,
            "ReportsBucket",
            bucket_name=f"rekon-reports-{self.account}-{self.region}",
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.kms_key,
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            removal_policy=RemovalPolicy.RETAIN,
        )
