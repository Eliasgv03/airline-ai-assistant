"""
LLM Service - Google Gemini Integration with Model Fallback

This service provides a centralized interface for interacting with Google's Gemini LLM.
It handles configuration, error handling, logging, and automatic model fallback.
"""

import logging

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMServiceError(Exception):
    """Custom exception for LLM service errors"""

    pass


def get_llm(temperature: float = 0.3, max_tokens: int | None = None) -> ChatGoogleGenerativeAI:
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
    if not settings.GOOGLE_API_KEY:
        raise LLMServiceError("GOOGLE_API_KEY is not configured.")

    api_key = settings.GOOGLE_API_KEY.strip()

    # Try each model in the pool
    last_error = None
    for model_name in settings.GEMINI_MODEL_POOL:
        try:
            logger.info(f"Attempting to initialize LLM with model: {model_name}")
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                max_output_tokens=max_tokens,
                google_api_key=api_key,
                max_retries=0,  # Disable automatic retries to control fallback manually
            )
            logger.info(
                f"✅ LLM initialized successfully: model={model_name}, temperature={temperature}"
            )
            return llm
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize model {model_name}: {str(e)}")
            last_error = e
            continue  # Try next model in pool

    # If all models failed
    error_msg = f"All models in pool failed. Last error: {str(last_error)}"
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
        logger.debug(f"Response length: {len(response.content)} chars")

        return response.content

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
