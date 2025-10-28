"""
Application Configuration
Loads environment variables and provides configuration settings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # AI Configuration - Local Claude CLI (no API keys needed!)
    use_claude_cli: bool = Field(default=True, env="USE_CLAUDE_CLI")
    claude_cli_command: str = Field(default="claude", env="CLAUDE_CLI_COMMAND")

    # API keys (optional - only if not using Claude CLI)
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-sonnet-4-20250514", env="ANTHROPIC_MODEL")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")

    # SQL Server Configuration
    db_driver: str = Field(default="ODBC Driver 18 for SQL Server", env="DB_DRIVER")
    db_server: str = Field(..., env="DB_SERVER")
    db_port: int = Field(default=1433, env="DB_PORT")
    db_name: str = Field(..., env="DB_NAME")
    db_user: Optional[str] = Field(default=None, env="DB_USER")
    db_password: Optional[str] = Field(default=None, env="DB_PASSWORD")
    db_trusted_connection: bool = Field(default=False, env="DB_TRUSTED_CONNECTION")
    db_connection_string: Optional[str] = Field(default=None, env="DB_CONNECTION_STRING")

    # Application Configuration
    app_name: str = Field(default="Text-to-SQL Application", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    app_host: str = Field(default="0.0.0.0", env="APP_HOST")
    app_port: int = Field(default=8000, env="APP_PORT")
    debug: bool = Field(default=False, env="DEBUG")

    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    require_confirmation_for_writes: bool = Field(default=True, env="REQUIRE_CONFIRMATION_FOR_WRITES")
    enable_admin_operations: bool = Field(default=False, env="ENABLE_ADMIN_OPERATIONS")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", env="LOG_FILE")

    # Query Limits
    max_rows_return: int = Field(default=1000, env="MAX_ROWS_RETURN")
    query_timeout_seconds: int = Field(default=30, env="QUERY_TIMEOUT_SECONDS")

    # Worker Service Configuration
    deployment_environment: str = Field(default="dev", env="DEPLOYMENT_ENVIRONMENT")
    batch_processing_size: int = Field(default=10, env="BATCH_PROCESSING_SIZE")

    # Teams Bot Configuration
    microsoft_app_id: Optional[str] = Field(default=None, env="MICROSOFT_APP_ID")
    microsoft_app_password: Optional[str] = Field(default=None, env="MICROSOFT_APP_PASSWORD")

    # Language Settings
    default_language: str = Field(default="en", env="DEFAULT_LANGUAGE")
    supported_languages: str = Field(default="en,he", env="SUPPORTED_LANGUAGES")

    # Queue Database (PostgreSQL)
    queue_db_host: str = Field(default="localhost", env="QUEUE_DB_HOST")
    queue_db_port: int = Field(default=5433, env="QUEUE_DB_PORT")
    queue_db_name: str = Field(default="text_to_sql_queue", env="QUEUE_DB_NAME")
    queue_db_user: str = Field(default="postgres", env="QUEUE_DB_USER")
    queue_db_password: str = Field(default="postgres", env="QUEUE_DB_PASSWORD")

    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_connection_string(self) -> str:
        """
        Build SQL Server connection string.
        If DB_CONNECTION_STRING is provided, use it directly.
        Otherwise, construct from individual components.
        """
        if self.db_connection_string:
            return self.db_connection_string

        if self.db_trusted_connection:
            # Windows Authentication
            conn_str = (
                f"mssql+pyodbc://@{self.db_server}:{self.db_port}/{self.db_name}"
                f"?driver={self.db_driver}&Trusted_Connection=yes"
            )
        else:
            # SQL Server Authentication
            if not self.db_user or not self.db_password:
                raise ValueError("DB_USER and DB_PASSWORD required when not using trusted connection")

            # URL-encode the driver name for SQLAlchemy
            from urllib.parse import quote_plus
            driver_encoded = quote_plus(self.db_driver)

            conn_str = (
                f"mssql+pyodbc://{self.db_user}:{self.db_password}"
                f"@{self.db_server}/{self.db_name}"
                f"?driver={driver_encoded}"
                f"&TrustServerCertificate=yes"
                f"&timeout=30"
            )

        return conn_str


# Global settings instance
settings = Settings()
