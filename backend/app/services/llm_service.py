"""
LLM Service - Google Gemini Integration

This service provides a centralized interface for interacting with Google's Gemini LLM.
It handles configuration, error handling, and logging for all LLM operations.
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
    Get configured LLM instance.

    Args:
        temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
        max_tokens: Maximum tokens in response (None = model default)

    Returns:
        Configured ChatGoogleGenerativeAI instance

    Raises:
        LLMServiceError: If API key is missing or configuration fails
    """
    if not settings.GOOGLE_API_KEY:
        raise LLMServiceError(
            "GOOGLE_API_KEY is not configured. "
            "Please set it in your .env file or environment variables."
        )

    try:
        llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            temperature=temperature,
            max_output_tokens=max_tokens,
            google_api_key=settings.GOOGLE_API_KEY,
        )
        logger.info(f"LLM initialized: model={settings.GEMINI_MODEL}, temperature={temperature}")
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {str(e)}")
        raise LLMServiceError(f"Failed to initialize LLM: {str(e)}") from e


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
