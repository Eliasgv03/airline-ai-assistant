"""
LLM Manager - Central Dispatcher for LLM Providers.

This module provides a provider-agnostic interface for LLM operations.
It reads the LLM_PROVIDER setting from config and routes calls to the
appropriate provider (Gemini, Groq, OpenAI, etc.).

Usage:
    from app.services.llm_manager import llm_manager

    # Invoke (with round-robin rotation on Gemini)
    response = llm_manager.invoke(messages)

    # Streaming
    async for chunk in llm_manager.astream(messages):
        yield chunk

To add a new provider:
    1. Create provider_service.py (e.g., openai_service.py)
    2. Implement ProviderClass with: name, get_llm, invoke, astream
    3. Add to PROVIDERS dict below
    4. Add LLM_PROVIDER option in config.py
"""

import logging
from typing import TYPE_CHECKING

from langchain_core.messages import AIMessage, BaseMessage

from app.core.config import get_settings
from app.services.llm_base import LLMServiceError

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMManager:
    """
    Central LLM Manager that dispatches to the configured provider.

    This class provides a unified interface regardless of which LLM provider
    is configured. It supports:
    - Gemini (with round-robin rotation)
    - Groq (high-speed alternative)
    - Future providers (OpenAI, Anthropic, etc.)

    The active provider is determined by the LLM_PROVIDER setting in config.
    """

    def __init__(self):
        self._providers: dict = {}
        self._active_provider = None
        self._initialized = False

    def _ensure_initialized(self):
        """Lazy initialization of providers."""
        if self._initialized:
            return

        # Import providers here to avoid circular imports
        from app.services.gemini_service import gemini_provider
        from app.services.groq_service import groq_provider

        self._providers = {
            "gemini": gemini_provider,
            "groq": groq_provider,
            # Add new providers here:
            # "openai": openai_provider,
        }

        provider_name = settings.LLM_PROVIDER.lower()
        if provider_name not in self._providers:
            available = ", ".join(self._providers.keys())
            raise LLMServiceError(
                f"Unknown LLM_PROVIDER: '{provider_name}'. Available: {available}"
            )

        self._active_provider = self._providers[provider_name]
        self._initialized = True
        logger.info(f"🤖 LLM Manager initialized with provider: {provider_name}")

    @property
    def provider(self):
        """Get the active provider instance."""
        self._ensure_initialized()
        return self._active_provider

    @property
    def provider_name(self) -> str:
        """Get the name of the active provider."""
        self._ensure_initialized()
        assert self._active_provider is not None
        return self._active_provider.name  # type: ignore[no-any-return]

    def get_llm(self, temperature: float = 0.3, model_name: str | None = None):
        """
        Get an LLM instance from the active provider.

        Args:
            temperature: Controls randomness
            model_name: Specific model to use

        Returns:
            LangChain-compatible LLM instance
        """
        self._ensure_initialized()
        assert self._active_provider is not None
        logger.debug(f"Getting LLM from {self.provider_name}")
        return self._active_provider.get_llm(
            temperature=temperature,
            model_name=model_name,
        )

    def invoke(
        self,
        messages: list[BaseMessage],
        temperature: float = 0.3,
        model_name: str | None = None,
        tools: list | None = None,
    ) -> AIMessage:
        """
        Invoke the LLM with the given messages.

        Uses round-robin rotation on Gemini, standard invocation on others.

        Args:
            messages: Conversation messages
            temperature: Controls randomness
            model_name: Specific model (None = use rotation on Gemini)
            tools: Optional tools to bind

        Returns:
            AIMessage response
        """
        self._ensure_initialized()
        assert self._active_provider is not None
        logger.info(f"🔄 Invoking LLM via {self.provider_name}")
        return self._active_provider.invoke(  # type: ignore[no-any-return]
            messages=messages,
            temperature=temperature,
            model_name=model_name,
            tools=tools,
        )

    async def astream(
        self,
        messages: list[BaseMessage],
        temperature: float = 0.3,
        tools: list | None = None,
    ):
        """
        Stream LLM responses asynchronously.

        Uses round-robin rotation on Gemini, standard streaming on others.

        Args:
            messages: Conversation messages
            temperature: Controls randomness
            tools: Optional tools to bind

        Yields:
            Response chunks
        """
        self._ensure_initialized()
        assert self._active_provider is not None
        logger.info(f"🔄 Streaming via {self.provider_name}")
        async for chunk in self._active_provider.astream(
            messages=messages,
            temperature=temperature,
            tools=tools,
        ):
            yield chunk


# Singleton instance for import
llm_manager = LLMManager()


# Re-export LLMServiceError for convenience
__all__ = ["llm_manager", "LLMManager", "LLMServiceError"]
