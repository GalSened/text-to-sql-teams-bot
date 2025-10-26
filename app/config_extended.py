"""
Extended configuration to support multiple AI providers.
Add these settings to your .env file.
"""
from app.config import settings as base_settings
from pydantic import Field
from typing import Optional


# Extend existing settings with AI provider configuration
class ExtendedSettings:
    """Extended settings with AI provider support."""

    # Anthropic (Claude) Configuration
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022", env="ANTHROPIC_MODEL")

    # AI Provider Selection
    primary_ai_provider: str = Field(default="claude", env="PRIMARY_AI_PROVIDER")
    fallback_ai_provider: str = Field(default="openai", env="FALLBACK_AI_PROVIDER")

    # Model Selection by Query Type
    simple_query_model: str = Field(default="claude-3-haiku-20240307", env="SIMPLE_QUERY_MODEL")
    complex_query_model: str = Field(default="claude-3-5-sonnet-20241022", env="COMPLEX_QUERY_MODEL")
    validation_model: str = Field(default="claude-3-5-sonnet-20241022", env="VALIDATION_MODEL")


# Add extended settings to base settings
for attr in dir(ExtendedSettings):
    if not attr.startswith('_'):
        value = getattr(ExtendedSettings, attr)
        if isinstance(value, Field):
            setattr(base_settings, attr, value.default)


def get_extended_settings():
    """Get settings with AI provider configuration."""
    return base_settings
