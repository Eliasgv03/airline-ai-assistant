"""
Base Protocol and Types for LLM Providers.

This module defines the interface that all LLM providers must implement.
To add a new provider (e.g., OpenAI), create a new file (openai_service.py)
and implement these protocols.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from langchain_core.messages import AIMessage, BaseMessage


class LLMServiceError(Exception):
    """Custom exception for LLM service errors."""

    pass


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    All LLM providers (Gemini, Groq, OpenAI, etc.) must implement this interface.
    This allows chat_service.py to be provider-agnostic.

    Example usage for a new provider:
        1. Create openai_service.py
        2. Implement OpenAIProvider(BaseLLMProvider)
        3. Register in llm_manager.py
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name (e.g., 'gemini', 'groq', 'openai')."""
        pass

    @abstractmethod
    def get_llm(
        self,
        temperature: float = 0.3,
        model_name: str | None = None,
    ):
        """
        Get an LLM instance for this provider.

        Args:
            temperature: Controls randomness (0.0-1.0)
            model_name: Specific model to use, or None for default

        Returns:
            A LangChain-compatible LLM instance
        """
        pass

    @abstractmethod
    def invoke(
        self,
        messages: list[BaseMessage],
        temperature: float = 0.3,
        model_name: str | None = None,
        tools: list | None = None,
    ) -> AIMessage:
        """
        Invoke the LLM with messages.

        Uses round-robin rotation and fallback on errors.

        Args:
            messages: Conversation messages
            temperature: Controls randomness
            model_name: Specific model (None = use rotation)
            tools: Optional tools to bind

        Returns:
            AIMessage response
        """
        pass

    @abstractmethod
    async def astream(
        self,
        messages: list[BaseMessage],
        temperature: float = 0.3,
        tools: list | None = None,
    ) -> AsyncGenerator:
        """
        Stream LLM responses asynchronously.

        Uses round-robin rotation and fallback on errors.

        Args:
            messages: Conversation messages
            temperature: Controls randomness
            tools: Optional tools to bind

        Yields:
            Response chunks
        """
        pass
