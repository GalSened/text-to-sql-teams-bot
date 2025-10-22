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

    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
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

            conn_str = (
                f"mssql+pyodbc://{self.db_user}:{self.db_password}"
                f"@{self.db_server}:{self.db_port}/{self.db_name}"
                f"?driver={self.db_driver}"
            )

        return conn_str


# Global settings instance
settings = Settings()
