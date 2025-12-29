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


def get_api_keys() -> list[tuple[str, str]]:
    """Get list of available API keys for fallback chain."""
    api_keys: list[tuple[str, str]] = []
    if settings.GOOGLE_API_KEY:
        api_keys.append((settings.GOOGLE_API_KEY.strip(), "GOOGLE_API_KEY"))
    if settings.GOOGLE_FALLBACK_API_KEY:
        api_keys.append((settings.GOOGLE_FALLBACK_API_KEY.strip(), "GOOGLE_FALLBACK_API_KEY"))
    return api_keys


# Global rotation index for round-robin distribution
_rotation_index: int = 0


def get_all_combinations() -> list[tuple[str, str, str, str]]:
    """
    Get all model+API combinations for round-robin rotation.

    Returns:
        List of (model_name, api_key, key_name, combo_id) tuples
        Ordered: Model1+API1, Model1+API2, Model2+API1, Model2+API2, ...
    """
    api_keys = get_api_keys()
    models = settings.GEMINI_MODEL_POOL
    combinations = []

    for model in models:
        for api_key, key_name in api_keys:
            # Create clear combo_id: "gemini-2.5-flash-lite (PRIMARY)" or "(FALLBACK)"
            api_label = "PRIMARY" if "FALLBACK" not in key_name else "FALLBACK"
            combo_id = f"{model} ({api_label})"
            combinations.append((model, api_key, key_name, combo_id))

    return combinations


def get_next_rotation_index(total_combinations: int) -> int:
    """Get the next index in the rotation and increment the global counter."""
    global _rotation_index
    current = _rotation_index
    _rotation_index = (_rotation_index + 1) % total_combinations
    return current


def invoke_with_api_fallback(
    messages: list[BaseMessage],
    temperature: float = 0.3,
    model_name: str | None = None,
    tools: list | None = None,
) -> AIMessage:
    """
    Invoke LLM with round-robin rotation and automatic fallback on errors.

    Each call starts at the next position in the rotation cycle (proactive distribution).
    If an error occurs, it continues to the next combination in the cycle.

    Args:
        messages: List of conversation messages
        temperature: Controls randomness
        model_name: Specific model to use (None = use pool with rotation)
        tools: Optional list of tools to bind

    Returns:
        AIMessage response

    Raises:
        LLMServiceError: If all API keys and models fail
    """
    # If specific model requested, use fallback-only mode (no rotation)
    if model_name:
        api_keys = get_api_keys()
        if not api_keys:
            raise LLMServiceError("No Google API key configured.")

        for api_key, key_name in api_keys:
            try:
                logger.info(f"🔄 Trying {model_name} with {key_name}...")
                llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    temperature=temperature,
                    google_api_key=api_key,  # type: ignore[arg-type]
                    max_retries=0,
                    timeout=30,
                )
                if tools:
                    llm = llm.bind_tools(tools)
                response = llm.invoke(messages)
                logger.info(f"✅ Success with {model_name} + {key_name}")
                return response  # type: ignore[return-value]
            except Exception as e:
                logger.warning(f"⚠️ {model_name} + {key_name} failed: {e}")
                continue
        raise LLMServiceError(f"All API keys failed for model {model_name}")

    # Round-robin rotation mode
    combinations = get_all_combinations()
    if not combinations:
        raise LLMServiceError("No API keys or models configured.")

    total = len(combinations)
    start_index = get_next_rotation_index(total)
    last_error: Exception | None = None

    logger.info(f"🔄 Round-robin: Starting at position {start_index + 1}/{total}")

    # Try all combinations starting from the rotation index
    for i in range(total):
        idx = (start_index + i) % total
        model, api_key, key_name, combo_id = combinations[idx]

        try:
            logger.info(f"🔄 [{idx + 1}/{total}] Trying {combo_id}...")

            llm = ChatGoogleGenerativeAI(
                model=model,
                temperature=temperature,
                google_api_key=api_key,  # type: ignore[arg-type]
                max_retries=0,
                timeout=30,
            )

            if tools:
                llm = llm.bind_tools(tools)

            response = llm.invoke(messages)
            logger.info(f"✅ Success with {combo_id}")
            return response  # type: ignore[return-value]

        except Exception as e:
            error_str = str(e)
            error_type = type(e).__name__

            if (
                "429" in error_str
                or "quota" in error_str.lower()
                or "ResourceExhausted" in error_type
            ):
                logger.warning(f"⚠️ Quota exhausted for {combo_id}, trying next...")
            else:
                logger.warning(f"⚠️ {combo_id} failed: {error_type}: {error_str[:100]}")

            last_error = e
            continue

    error_msg = f"All {total} combinations exhausted. Last error: {last_error}"
    logger.error(f"❌ {error_msg}")
    raise LLMServiceError(error_msg) from last_error


async def astream_with_api_fallback(
    messages: list[BaseMessage],
    temperature: float = 0.3,
    tools: list | None = None,
):
    """
    Async streaming with round-robin rotation and automatic fallback.

    Each call starts at the next position in the rotation cycle (proactive distribution).
    If an error occurs, it continues to the next combination.

    Args:
        messages: List of conversation messages
        temperature: Controls randomness
        tools: Optional list of tools to bind

    Yields:
        Chunks from the streaming response

    Raises:
        LLMServiceError: If all API keys and models fail
    """
    # Round-robin rotation mode
    combinations = get_all_combinations()
    if not combinations:
        raise LLMServiceError("No API keys or models configured.")

    total = len(combinations)
    start_index = get_next_rotation_index(total)
    last_error: Exception | None = None

    logger.info(f"🔄 Streaming round-robin: Starting at position {start_index + 1}/{total}")

    # Try all combinations starting from the rotation index
    for i in range(total):
        idx = (start_index + i) % total
        model, api_key, key_name, combo_id = combinations[idx]

        try:
            logger.info(f"🔄 Streaming [{idx + 1}/{total}]: Trying {combo_id}...")

            llm = ChatGoogleGenerativeAI(
                model=model,
                temperature=temperature,
                google_api_key=api_key,  # type: ignore[arg-type]
                max_retries=0,
                timeout=30,
            )

            if tools:
                llm = llm.bind_tools(tools)

            # Stream - yield chunks as they come
            async for chunk in llm.astream(messages):
                yield chunk

            # If we got here without error, we're done
            logger.info(f"✅ Streaming success with {combo_id}")
            return

        except Exception as e:
            error_str = str(e)
            error_type = type(e).__name__

            if (
                "429" in error_str
                or "quota" in error_str.lower()
                or "ResourceExhausted" in error_type
            ):
                logger.warning(f"⚠️ Quota exhausted for {combo_id}, trying next...")
            else:
                logger.warning(f"⚠️ Streaming failed {combo_id}: {error_type}: {error_str[:100]}")

            last_error = e
            continue

    error_msg = f"All {total} combinations exhausted for streaming. Last error: {last_error}"
    logger.error(f"❌ {error_msg}")
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


# =============================================================================
# GeminiProvider Class - Implements BaseLLMProvider Interface
# =============================================================================


class GeminiProvider:
    """
    Gemini LLM Provider implementing the BaseLLMProvider interface.

    This class wraps the existing gemini functions to provide a unified
    interface that llm_manager.py can use.
    """

    @property
    def name(self) -> str:
        """Return provider name."""
        return "gemini"

    def get_llm(
        self,
        temperature: float = 0.3,
        model_name: str | None = None,
    ) -> ChatGoogleGenerativeAI:
        """Get a Gemini LLM instance."""
        return get_llm(temperature=temperature, model_name=model_name)

    def invoke(
        self,
        messages: list[BaseMessage],
        temperature: float = 0.3,
        model_name: str | None = None,
        tools: list | None = None,
    ) -> AIMessage:
        """
        Invoke Gemini with round-robin rotation and fallback.

        Uses invoke_with_api_fallback internally.
        """
        return invoke_with_api_fallback(
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
        Async streaming with round-robin rotation and fallback.

        Uses astream_with_api_fallback internally.
        """
        async for chunk in astream_with_api_fallback(
            messages=messages,
            temperature=temperature,
            tools=tools,
        ):
            yield chunk


# Singleton instance for easy import
gemini_provider = GeminiProvider()
