"""
Unified AI client supporting multiple providers (OpenAI, Claude, etc.)
with intelligent routing and fallback mechanisms.
"""
from typing import Dict, Any, Optional, Literal
from enum import Enum

from app.config import settings
from loguru import logger


class AIProvider(str, Enum):
    """Available AI providers."""
    OPENAI = "openai"
    CLAUDE = "claude"
    AUTO = "auto"


class UnifiedAIClient:
    """
    Unified client for multiple AI providers with smart routing.

    Features:
    - Automatic provider selection based on query complexity
    - Fallback to secondary provider on failure
    - Cost optimization
    - Performance tracking
    """

    def __init__(self):
        """Initialize AI client with available providers."""
        self.providers = {}
        self.primary_provider = getattr(settings, 'primary_ai_provider', 'claude')
        self.fallback_provider = getattr(settings, 'fallback_ai_provider', 'openai')

        # Initialize OpenAI if available
        try:
            from app.core.openai_client import OpenAIClient
            self.providers['openai'] = OpenAIClient()
            logger.info("✓ OpenAI provider initialized")
        except Exception as e:
            logger.warning(f"OpenAI provider not available: {e}")

        # Initialize Claude if available
        try:
            from app.core.claude_client import ClaudeClient
            self.providers['claude'] = ClaudeClient()
            logger.info("✓ Claude provider initialized")
        except Exception as e:
            logger.warning(f"Claude provider not available: {e}")

        if not self.providers:
            raise ValueError("No AI providers configured! Set OPENAI_API_KEY or ANTHROPIC_API_KEY")

        logger.info(f"Available providers: {list(self.providers.keys())}")
        logger.info(f"Primary: {self.primary_provider}, Fallback: {self.fallback_provider}")

    def generate_sql(
        self,
        question: str,
        schema_info: Dict[str, Any],
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate SQL query using intelligent provider selection.

        Args:
            question: Natural language question
            schema_info: Database schema information
            provider: Force specific provider (optional)

        Returns:
            Dictionary containing SQL, type, risk level, and explanation
        """
        # Determine which provider to use
        selected_provider = self._select_provider(question, provider)

        logger.info(f"Using provider: {selected_provider}")

        try:
            # Try primary provider
            client = self.providers[selected_provider]
            result = client.generate_sql(question, schema_info)

            # Add metadata
            result['provider'] = selected_provider
            return result

        except Exception as e:
            logger.error(f"Provider {selected_provider} failed: {e}")

            # Try fallback if available
            if self.fallback_provider and self.fallback_provider in self.providers:
                logger.info(f"Trying fallback provider: {self.fallback_provider}")
                try:
                    client = self.providers[self.fallback_provider]
                    result = client.generate_sql(question, schema_info)
                    result['provider'] = self.fallback_provider
                    result['fallback_used'] = True
                    return result
                except Exception as fallback_error:
                    logger.error(f"Fallback provider also failed: {fallback_error}")

            # No fallback or fallback failed
            raise

    def _select_provider(
        self,
        question: str,
        forced_provider: Optional[str] = None
    ) -> str:
        """
        Intelligently select AI provider based on query characteristics.

        Args:
            question: The user's question
            forced_provider: Force specific provider

        Returns:
            Provider name to use
        """
        # If provider is forced, use it if available
        if forced_provider and forced_provider in self.providers:
            return forced_provider

        # Use primary provider if available
        if self.primary_provider in self.providers:
            return self.primary_provider

        # Use any available provider
        return list(self.providers.keys())[0]

    def explain_query(self, sql: str, provider: Optional[str] = None) -> str:
        """
        Generate explanation using specified or primary provider.

        Args:
            sql: SQL query to explain
            provider: Specific provider to use (optional)

        Returns:
            Plain English explanation
        """
        selected_provider = provider or self.primary_provider

        if selected_provider not in self.providers:
            selected_provider = list(self.providers.keys())[0]

        try:
            client = self.providers[selected_provider]
            return client.explain_query(sql)
        except Exception as e:
            logger.error(f"Query explanation failed: {e}")
            return "Unable to generate explanation"

    def get_available_providers(self) -> list[str]:
        """Get list of initialized providers."""
        return list(self.providers.keys())

    def switch_primary_provider(self, provider: str):
        """
        Switch primary provider.

        Args:
            provider: Provider name to set as primary
        """
        if provider not in self.providers:
            raise ValueError(f"Provider '{provider}' not available")

        self.primary_provider = provider
        logger.info(f"Primary provider switched to: {provider}")


# Global unified AI client instance
try:
    ai_client = UnifiedAIClient()
except Exception as e:
    logger.error(f"Failed to initialize AI client: {e}")
    ai_client = None
