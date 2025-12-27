"""
LLM Service - Google Gemini Integration with Model Fallback

This service provides a centralized interface for interacting with Google's Gemini LLM.
It handles configuration, error handling, logging, and automatic model fallback.
"""

import logging
import os

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMServiceError(Exception):
    """Custom exception for LLM service errors"""

    pass


def get_llm(
    temperature: float = 0.3, max_tokens: int | None = None, model_name: str | None = None
) -> ChatGoogleGenerativeAI:
    """
    Get configured LLM instance with automatic model fallback.

    Args:
        temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
        max_tokens: Maximum tokens in response (None = model default)

    Returns:
        Configured ChatGoogleGenerativeAI instance

    Raises:
        LLMServiceError: If API key is missing or all models in pool fail
    """
    # Configure LangSmith tracing if enabled
    if settings.is_tracing_enabled:
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API_KEY or ""
        os.environ["LANGSMITH_PROJECT"] = settings.LANGSMITH_PROJECT
        os.environ["LANGSMITH_ENDPOINT"] = settings.LANGSMITH_ENDPOINT
        logger.info("🔍 LangSmith tracing enabled for Gemini")

    # Build list of available API keys (fallback chain)
    api_keys: list[tuple[str, str]] = []  # (key, description)

    if settings.GOOGLE_API_KEY:
        api_keys.append((settings.GOOGLE_API_KEY.strip(), "GOOGLE_API_KEY"))
    if settings.GOOGLE_FALLBACK_API_KEY:
        api_keys.append((settings.GOOGLE_FALLBACK_API_KEY.strip(), "GOOGLE_FALLBACK_API_KEY"))

    if not api_keys:
        raise LLMServiceError(
            "No Google API key configured. Set GOOGLE_API_KEY or GOOGLE_FALLBACK_API_KEY."
        )

    # Determine which models to try
    models_to_try = [model_name] if model_name else settings.GEMINI_MODEL_POOL

    # Try each API key, and for each key try each model
    last_error: Exception | None = None
    for api_key, key_name in api_keys:
        for model in models_to_try:
            try:
                logger.info(f"Attempting LLM init: {key_name} with model {model}")
                llm = ChatGoogleGenerativeAI(
                    model=model,
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    google_api_key=api_key,  # type: ignore[arg-type]
                    max_retries=0,  # Disable internal retries - let our fallback handle it
                    timeout=30,  # 30 second timeout per request
                )  # type: ignore
                logger.info(f"✅ LLM initialized: {key_name}, model={model}")
                return llm
            except Exception as e:
                logger.warning(f"⚠️ {key_name} + model {model} failed: {str(e)}")
                last_error = e
                continue  # Try next model or key

    # If all keys and models failed
    error_msg = f"All API keys and models failed. Last error: {str(last_error)}"
    logger.error(error_msg)
    raise LLMServiceError(error_msg) from last_error


def chat_complete(
    messages: list[BaseMessage],
    temperature: float = 0.3,
    max_tokens: int | None = None,
) -> str:
    """
    Generate a chat completion using the LLM.

    Args:
        messages: List of conversation messages (SystemMessage, HumanMessage, AIMessage)
        temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
        max_tokens: Maximum tokens in response

    Returns:
        Generated response text

    Raises:
        LLMServiceError: If LLM call fails
    """
    try:
        llm = get_llm(temperature=temperature, max_tokens=max_tokens)

        logger.info(f"Generating completion with {len(messages)} messages")
        logger.debug(f"Messages: {[msg.type for msg in messages]}")

        # Invoke the LLM
        response = llm.invoke(messages)

        logger.info("Completion generated successfully")
        logger.debug(f"Response length: {len(str(response.content))} chars")

        # Handle response content which can be str or list
        content = response.content
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            # If content is a list, join string elements
            return " ".join(str(item) for item in content if isinstance(item, str))
        else:
            return str(content)

    except LLMServiceError:
        # Re-raise our custom errors
        raise
    except Exception as e:
        logger.error(f"LLM completion failed: {str(e)}")
        raise LLMServiceError(f"Failed to generate completion: {str(e)}") from e


def create_message(role: str, content: str) -> BaseMessage:
    """
    Create a message object for the LLM.

    Args:
        role: Message role ('system', 'user', 'assistant')
        content: Message content

    Returns:
        Appropriate message object

    Raises:
        ValueError: If role is invalid
    """
    if role == "system":
        return SystemMessage(content=content)
    elif role == "user":
        return HumanMessage(content=content)
    elif role == "assistant":
        return AIMessage(content=content)
    else:
        raise ValueError(f"Invalid role: {role}. Must be 'system', 'user', or 'assistant'")
