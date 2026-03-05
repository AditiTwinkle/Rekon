"""ElastiCache Redis stack for caching."""

from aws_cdk import (
    aws_elasticache as elasticache,
    aws_ec2 as ec2,
)
from constructs import Construct

from infrastructure.stacks.base_stack import BaseStack


class CacheStack(BaseStack):
    """ElastiCache Redis stack for caching."""

    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, **kwargs) -> None:
        """Initialize cache stack.

        Args:
            scope: CDK scope
            id: Stack ID
            vpc: VPC for cache
            **kwargs: Additional stack properties
        """
        super().__init__(scope, id, **kwargs)

        self.vpc = vpc

        # Create security group for Redis
        self.cache_security_group = ec2.SecurityGroup(
            self,
            "CacheSecurityGroup",
            vpc=vpc,
            description="Security group for Rekon Redis cache",
            allow_all_outbound=True,
        )

        # Allow Redis access from within VPC
        self.cache_security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(6379),
            description="Redis from VPC",
        )

        # Create Redis subnet group
        subnet_ids = [subnet.subnet_id for subnet in vpc.private_subnets]

        # Create Redis cluster using L1 construct (CDK doesn't have full L2 support for ElastiCache)
        self.redis_cluster = elasticache.CfnCacheCluster(
            self,
            "RedisCluster",
            cache_node_type="cache.t3.micro",
            engine="redis",
            num_cache_nodes=1,
            port=6379,
            vpc_security_group_ids=[self.cache_security_group.security_group_id],
            cache_subnet_group_name=self._create_subnet_group(subnet_ids).ref,
            auto_minor_version_upgrade=True,
            engine_version="7.0",
            at_rest_encryption_enabled=True,
            transit_encryption_enabled=True,
        )

    def _create_subnet_group(self, subnet_ids: list) -> elasticache.CfnSubnetGroup:
        """Create ElastiCache subnet group.

        Args:
            subnet_ids: List of subnet IDs

        Returns:
            Subnet group
        """
        return elasticache.CfnSubnetGroup(
            self,
            "RedisSubnetGroup",
            description="Subnet group for Rekon Redis",
            subnet_ids=subnet_ids,
        )
