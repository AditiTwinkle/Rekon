"""RDS PostgreSQL Aurora database stack."""

from aws_cdk import (
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_secretsmanager as secretsmanager,
    RemovalPolicy,
)
from constructs import Construct

from infrastructure.stacks.base_stack import BaseStack


class DatabaseStack(BaseStack):
    """RDS PostgreSQL Aurora database stack."""

    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, **kwargs) -> None:
        """Initialize database stack.

        Args:
            scope: CDK scope
            id: Stack ID
            vpc: VPC for database
            **kwargs: Additional stack properties
        """
        super().__init__(scope, id, **kwargs)

        self.vpc = vpc

        # Create security group for database
        self.db_security_group = ec2.SecurityGroup(
            self,
            "DBSecurityGroup",
            vpc=vpc,
            description="Security group for Rekon RDS database",
            allow_all_outbound=True,
        )

        # Allow PostgreSQL access from within VPC
        self.db_security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(5432),
            description="PostgreSQL from VPC",
        )

        # Create database credentials secret
        self.db_secret = secretsmanager.Secret(
            self,
            "DBSecret",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"username": "rekon"}',
                generate_string_key="password",
                password_length=32,
                exclude_characters="/@\"\\",
            ),
        )

        # Create Aurora PostgreSQL cluster
        self.cluster = rds.DatabaseCluster(
            self,
            "RekonCluster",
            engine=rds.DatabaseClusterEngine.aurora_postgres(
                version=rds.AuroraPostgresEngineVersion.VER_15_2,
            ),
            credentials=rds.Credentials.from_secret(self.db_secret),
            writer=rds.ClusterInstance(
                instance_type=ec2.InstanceType.of(
                    instance_class=ec2.InstanceClass.BURSTABLE3,
                    instance_size=ec2.InstanceSize.MICRO,
                ),
                is_writer=True,
                publicly_accessible=False,
            ),
            readers=[
                rds.ClusterInstance(
                    instance_type=ec2.InstanceType.of(
                        instance_class=ec2.InstanceClass.BURSTABLE3,
                        instance_size=ec2.InstanceSize.MICRO,
                    ),
                    is_writer=False,
                    publicly_accessible=False,
                )
            ],
            vpc=vpc,
            security_group=self.db_security_group,
            backup=rds.BackupProps(
                retention=RemovalPolicy.RETAIN,
            ),
            removal_policy=RemovalPolicy.SNAPSHOT,
            default_database_name="rekon",
            multi_az=True,
            storage_encrypted=True,
            enable_cloudwatch_logs_exports=["postgresql"],
        )

        # Create database schema
        self._create_database_schema()

    def _create_database_schema(self) -> None:
        """Create database schema."""
        # Schema creation will be handled by Alembic migrations
        # This is a placeholder for future migration setup
        pass
