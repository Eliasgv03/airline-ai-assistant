"""
Unified LLM Service - Provider-Agnostic Interface

This service provides a unified interface for both Gemini and Groq LLMs,
allowing easy switching between providers via configuration.
"""

import logging

from langchain_core.messages import AIMessage, BaseMessage

from app.core.config import get_settings
from app.services.gemini_service import LLMServiceError, get_llm
from app.services.groq_service import GroqServiceError, get_groq_llm

logger = logging.getLogger(__name__)
settings = get_settings()


class UnifiedLLMError(Exception):
    """Custom exception for unified LLM errors"""

    pass


def get_unified_llm(temperature: float = 0.3, max_tokens: int | None = None):
    """
    Get LLM instance based on configured provider.

    Args:
        temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
        max_tokens: Maximum tokens in response

    Returns:
        Configured LLM instance (Gemini or Groq)

    Raises:
        UnifiedLLMError: If provider is invalid or initialization fails
    """
    provider = settings.LLM_PROVIDER.lower()

    logger.info(f"Initializing LLM with provider: {provider}")

    try:
        if provider == "gemini":
            return get_llm(temperature=temperature, max_tokens=max_tokens)
        elif provider == "groq":
            return get_groq_llm(temperature=temperature, max_tokens=max_tokens)
        else:
            raise UnifiedLLMError(f"Invalid LLM provider: {provider}. Must be 'gemini' or 'groq'")
    except (LLMServiceError, GroqServiceError) as e:
        logger.error(f"Failed to initialize {provider} LLM: {str(e)}")
        raise UnifiedLLMError(f"LLM initialization failed: {str(e)}") from e


def invoke_with_fallback_provider(messages: list[BaseMessage]) -> AIMessage:
    """
    Invoke LLM with automatic provider fallback.

    First tries the configured provider, then falls back to the alternative.

    Args:
        messages: List of conversation messages

    Returns:
        AI response message

    Raises:
        UnifiedLLMError: If both providers fail
    """
    primary_provider = settings.LLM_PROVIDER.lower()
    fallback_provider = "groq" if primary_provider == "gemini" else "gemini"

    # Try primary provider
    try:
        logger.info(f"Attempting primary provider: {primary_provider}")
        llm = get_unified_llm()
        response = llm.invoke(messages)
        logger.info(f"✅ {primary_provider} succeeded")
        return response
    except Exception as e:
        logger.warning(f"⚠️ {primary_provider} failed: {str(e)}")

        # Try fallback provider
        try:
            logger.info(f"Attempting fallback provider: {fallback_provider}")
            # Temporarily switch provider
            original_provider = settings.LLM_PROVIDER
            settings.LLM_PROVIDER = fallback_provider

            llm = get_unified_llm()
            response = llm.invoke(messages)

            # Restore original provider
            settings.LLM_PROVIDER = original_provider

            logger.info(f"✅ {fallback_provider} succeeded (fallback)")
            return response
        except Exception as fallback_error:
            logger.error(f"❌ {fallback_provider} also failed: {str(fallback_error)}")

            # Restore original provider
            settings.LLM_PROVIDER = original_provider

            raise UnifiedLLMError(
                f"Both providers failed. {primary_provider}: {str(e)}, "
                f"{fallback_provider}: {str(fallback_error)}"
            ) from fallback_error
