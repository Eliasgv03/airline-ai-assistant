"""
Groq LLM Service - High-Performance Alternative to Gemini

This service provides integration with Groq's ultra-fast LLM API.
Groq offers generous free tier quotas and extremely low latency.
"""

import logging
import os

from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GroqServiceError(Exception):
    """Custom exception for Groq service errors"""

    pass


def get_groq_llm(
    temperature: float = 0.3, max_tokens: int | None = None, model_name: str | None = None
) -> ChatGroq:
    """
    Get configured Groq LLM instance with automatic model fallback.

    Args:
        temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
        max_tokens: Maximum tokens in response (None = model default)
        model_name: Specific model to use (None = use pool)

    Returns:
        Configured ChatGroq instance

    Raises:
        GroqServiceError: If API key is missing or all models in pool fail
    """
    # Configure LangSmith tracing if enabled
    if settings.is_tracing_enabled:
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API_KEY or ""
        os.environ["LANGSMITH_PROJECT"] = settings.LANGSMITH_PROJECT
        os.environ["LANGSMITH_ENDPOINT"] = settings.LANGSMITH_ENDPOINT
        logger.info("🔍 LangSmith tracing enabled for Groq")

    if not settings.GROQ_API_KEY:
        raise GroqServiceError("GROQ_API_KEY is not configured.")

    api_key = settings.GROQ_API_KEY.strip()

    # Determine which models to try
    models_to_try = [model_name] if model_name else settings.GROQ_MODEL_POOL

    # Try each model in the pool
    last_error = None
    for model in models_to_try:
        try:
            logger.info(f"Attempting to initialize Groq LLM with model: {model}")
            llm = ChatGroq(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                groq_api_key=api_key,
                max_retries=2,
            )
            logger.info(
                f"✅ Groq LLM initialized successfully: model={model}, temperature={temperature}"
            )
            return llm
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Groq model {model}: {str(e)}")
            last_error = e
            continue  # Try next model in pool

    # If all models failed
    error_msg = f"All Groq models in pool failed. Last error: {str(last_error)}"
    logger.error(error_msg)
    raise GroqServiceError(error_msg) from last_error


def chat_complete_groq(
    messages: list[BaseMessage],
    temperature: float = 0.3,
    max_tokens: int | None = None,
) -> str:
    """
    Generate a chat completion using Groq LLM.

    Args:
        messages: List of conversation messages (SystemMessage, HumanMessage, AIMessage)
        temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
        max_tokens: Maximum tokens in response

    Returns:
        Generated response text

    Raises:
        GroqServiceError: If LLM call fails
    """
    try:
        llm = get_groq_llm(temperature=temperature, max_tokens=max_tokens)

        logger.info(f"Generating Groq completion with {len(messages)} messages")
        logger.debug(f"Messages: {[msg.type for msg in messages]}")

        # Invoke the LLM
        response = llm.invoke(messages)

        logger.info("Groq completion generated successfully")
        logger.debug(f"Response length: {len(response.content)} chars")

        return response.content

    except GroqServiceError:
        # Re-raise our custom errors
        raise
    except Exception as e:
        logger.error(f"Groq LLM completion failed: {str(e)}")
        raise GroqServiceError(f"Failed to generate completion: {str(e)}") from e
