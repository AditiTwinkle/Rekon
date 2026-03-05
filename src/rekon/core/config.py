"""Application configuration management."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # AWS Configuration
    aws_region: str = "us-east-1"
    aws_account_id: str = "123456789012"

    # Database Configuration
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "rekon"
    db_user: str = "rekon"
    db_password: str = "changeme"

    @property
    def database_url(self) -> str:
        """Construct database URL."""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    @property
    def redis_url(self) -> str:
        """Construct Redis URL."""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # Bedrock Configuration
    bedrock_region: str = "us-east-1"
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    api_title: str = "Rekon API"
    api_version: str = "0.1.0"

    # Cognito Configuration
    cognito_domain: str = "rekon-dev"
    cognito_client_id: str = ""
    cognito_client_secret: str = ""

    # S3 Configuration
    s3_bucket_name: str = "rekon-evidence"
    s3_region: str = "us-east-1"

    # Logging Configuration
    log_level: str = "INFO"

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


settings = Settings()
