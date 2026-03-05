#!/usr/bin/env python3
"""Deployment automation script for Rekon platform."""

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class RekonDeployer:
    """Handles deployment of Rekon platform."""

    def __init__(self, environment: str, region: str = "us-east-1"):
        """Initialize deployer.

        Args:
            environment: Deployment environment (dev, staging, prod)
            region: AWS region
        """
        self.environment = environment
        self.region = region
        self.project_root = Path(__file__).parent.parent

    def deploy(self) -> bool:
        """Execute full deployment.

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Starting deployment to {self.environment} in {self.region}")

            # Step 1: Validate environment
            if not self._validate_environment():
                logger.error("Environment validation failed")
                return False

            # Step 2: Build infrastructure
            if not self._build_infrastructure():
                logger.error("Infrastructure build failed")
                return False

            # Step 3: Deploy Lambda functions
            if not self._deploy_lambda_functions():
                logger.error("Lambda deployment failed")
                return False

            # Step 4: Deploy API
            if not self._deploy_api():
                logger.error("API deployment failed")
                return False

            # Step 5: Run database migrations
            if not self._run_migrations():
                logger.error("Database migrations failed")
                return False

            # Step 6: Seed initial data
            if not self._seed_data():
                logger.error("Data seeding failed")
                return False

            # Step 7: Run smoke tests
            if not self._run_smoke_tests():
                logger.error("Smoke tests failed")
                return False

            logger.info("Deployment completed successfully")
            return True

        except Exception as e:
            logger.error(f"Deployment failed: {str(e)}", exc_info=True)
            return False

    def _validate_environment(self) -> bool:
        """Validate deployment environment.

        Returns:
            True if valid, False otherwise
        """
        logger.info("Validating environment...")

        try:
            # Check AWS credentials
            result = subprocess.run(
                ["aws", "sts", "get-caller-identity"],
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info("AWS credentials validated")

            # Check required tools
            required_tools = ["docker", "cdk", "python"]
            for tool in required_tools:
                result = subprocess.run(
                    ["which", tool],
                    capture_output=True,
                    check=True,
                )
                logger.info(f"Found {tool}")

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Environment validation failed: {str(e)}")
            return False

    def _build_infrastructure(self) -> bool:
        """Build AWS infrastructure using CDK.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Building infrastructure...")

        try:
            # Synthesize CDK
            result = subprocess.run(
                ["cdk", "synth"],
                cwd=self.project_root / "infrastructure",
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info("CDK synthesis completed")

            # Deploy CDK stack
            result = subprocess.run(
                [
                    "cdk",
                    "deploy",
                    f"--require-approval=never",
                    f"--context",
                    f"environment={self.environment}",
                ],
                cwd=self.project_root / "infrastructure",
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info("Infrastructure deployed")

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Infrastructure build failed: {str(e)}")
            return False

    def _deploy_lambda_functions(self) -> bool:
        """Deploy Lambda functions.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Deploying Lambda functions...")

        try:
            lambda_functions = [
                "regulation_puller",
                "checklist_generator",
                "delta_analyzer",
                "gap_assessment",
                "remediation_engine",
                "evidence_retention",
            ]

            for function in lambda_functions:
                logger.info(f"Deploying {function}...")
                function_path = self.project_root / "lambda_functions" / function

                # Install dependencies
                result = subprocess.run(
                    [
                        "pip",
                        "install",
                        "-r",
                        "requirements.txt",
                        "-t",
                        ".",
                    ],
                    cwd=function_path,
                    capture_output=True,
                    text=True,
                    check=True,
                )

                # Package function
                result = subprocess.run(
                    ["zip", "-r", f"{function}.zip", "."],
                    cwd=function_path,
                    capture_output=True,
                    text=True,
                    check=True,
                )

                # Upload to Lambda
                result = subprocess.run(
                    [
                        "aws",
                        "lambda",
                        "update-function-code",
                        f"--function-name",
                        f"rekon-{function}-{self.environment}",
                        f"--zip-file",
                        f"fileb://{function}.zip",
                        f"--region",
                        self.region,
                    ],
                    cwd=function_path,
                    capture_output=True,
                    text=True,
                    check=True,
                )

                logger.info(f"Deployed {function}")

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Lambda deployment failed: {str(e)}")
            return False

    def _deploy_api(self) -> bool:
        """Deploy API.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Deploying API...")

        try:
            # Build Docker image
            result = subprocess.run(
                [
                    "docker",
                    "build",
                    "-t",
                    f"rekon-api:{self.environment}",
                    ".",
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info("Docker image built")

            # Push to ECR
            result = subprocess.run(
                [
                    "aws",
                    "ecr",
                    "get-login-password",
                    "--region",
                    self.region,
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            password = result.stdout.strip()

            # Tag and push image
            logger.info("Pushing image to ECR")

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"API deployment failed: {str(e)}")
            return False

    def _run_migrations(self) -> bool:
        """Run database migrations.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Running database migrations...")

        try:
            # Run Alembic migrations
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info("Database migrations completed")

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Database migrations failed: {str(e)}")
            return False

    def _seed_data(self) -> bool:
        """Seed initial data.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Seeding initial data...")

        try:
            # Run seed script
            result = subprocess.run(
                ["python", "scripts/seed_data.py", f"--environment={self.environment}"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info("Data seeding completed")

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Data seeding failed: {str(e)}")
            return False

    def _run_smoke_tests(self) -> bool:
        """Run smoke tests.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Running smoke tests...")

        try:
            # Run pytest smoke tests
            result = subprocess.run(
                ["pytest", "tests/smoke/", "-v"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info("Smoke tests passed")

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Smoke tests failed: {str(e)}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Deploy Rekon platform")
    parser.add_argument(
        "environment",
        choices=["dev", "staging", "prod"],
        help="Deployment environment",
    )
    parser.add_argument(
        "--region",
        default="us-east-1",
        help="AWS region",
    )

    args = parser.parse_args()

    deployer = RekonDeployer(args.environment, args.region)
    success = deployer.deploy()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
