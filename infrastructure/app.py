"""AWS CDK application entry point."""

from aws_cdk import App

from infrastructure.stacks.vpc_stack import VpcStack
from infrastructure.stacks.database_stack import DatabaseStack
from infrastructure.stacks.storage_stack import StorageStack
from infrastructure.stacks.dynamodb_stack import DynamoDBStack
from infrastructure.stacks.cache_stack import CacheStack
from infrastructure.stacks.events_stack import EventsStack

app = App()

region = app.node.try_get_context("region") or "us-east-1"
env = {"region": region}

# Create VPC stack
vpc_stack = VpcStack(
    app,
    "RekonVpcStack",
    env=env,
)

# Create database stack
database_stack = DatabaseStack(
    app,
    "RekonDatabaseStack",
    vpc=vpc_stack.vpc,
    env=env,
)
database_stack.add_dependency(vpc_stack)

# Create storage stack
storage_stack = StorageStack(
    app,
    "RekonStorageStack",
    env=env,
)

# Create DynamoDB stack
dynamodb_stack = DynamoDBStack(
    app,
    "RekonDynamoDBStack",
    env=env,
)

# Create cache stack
cache_stack = CacheStack(
    app,
    "RekonCacheStack",
    vpc=vpc_stack.vpc,
    env=env,
)
cache_stack.add_dependency(vpc_stack)

# Create events stack
events_stack = EventsStack(
    app,
    "RekonEventsStack",
    env=env,
)

app.synth()
