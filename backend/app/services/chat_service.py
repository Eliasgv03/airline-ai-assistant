"""
Chat Service - Orchestrates conversation flow with RAG and LLM

This service integrates memory, vector search, and LLM to provide contextual responses.
"""

import logging
import time
from typing import cast

from langchain.schema import AIMessage, SystemMessage
from langchain_core.messages import BaseMessage, ToolMessage
from langsmith import traceable

from app.core.config import get_settings
from app.prompts.system_prompts import get_system_prompt
from app.services.gemini_service import LLMServiceError, get_llm
from app.services.language_service import detect_language, get_language_instruction
from app.services.memory_service import get_memory_service
from app.services.vector_service import get_vector_service
from app.tools import ALL_TOOLS

logger = logging.getLogger(__name__)
settings = get_settings()


def wait_for_vector_service(max_wait_seconds: int = 120) -> None:
    """
    Wait for the VectorService to be ready (embedding model loaded).
    This is needed because the model is loaded in a background thread at startup.
    """
    from app.main import _model_loading_status

    start_time = time.time()
    check_interval = 0.5  # Check every 500ms

    while time.time() - start_time < max_wait_seconds:
        if _model_loading_status["completed"]:
            logger.info("✅ VectorService is ready")
            return

        if _model_loading_status["error"]:
            raise RuntimeError(f"VectorService failed to load: {_model_loading_status['error']}")

        elapsed = int(time.time() - start_time)
        if elapsed > 0 and elapsed % 10 == 0:  # Log every 10 seconds
            logger.info(f"⏳ Waiting for VectorService... ({elapsed}s elapsed)")

        time.sleep(check_interval)

    raise TimeoutError(f"VectorService did not become ready within {max_wait_seconds} seconds")


class ChatService:
    """Service for handling chat interactions with RAG and tool support"""

    def __init__(self):
        self.memory_service = get_memory_service()

        # Wait for vector service to be ready (model loaded in background thread)
        wait_for_vector_service()
        self.vector_service = get_vector_service()  # Use singleton - model loaded once

        self.tools = ALL_TOOLS
        self._session_languages: dict[str, str] = {}  # Track language per session
        logger.info(f"ChatService initialized with RAG support and {len(self.tools)} tools")

    def _invoke_with_fallback(self, messages) -> AIMessage:
        """
        Invoke LLM with automatic fallback across models AND providers.

        Strategy:
        1. Try all models in current provider's pool
        2. If all fail, try alternative provider
        """
        from app.services.llm_manager import invoke_with_fallback_provider

        provider = settings.LLM_PROVIDER
        logger.info(f"Using LLM provider: {provider}")

        # Get model pool based on provider
        if provider == "gemini":
            model_pool = settings.GEMINI_MODEL_POOL
        elif provider == "groq":
            model_pool = settings.GROQ_MODEL_POOL
        else:
            model_pool = settings.GEMINI_MODEL_POOL  # Default to Gemini

        last_error = None
        for model_name in model_pool:
            try:
                # Get LLM for specific model
                if provider == "gemini":
                    from app.services.gemini_service import get_llm

                    llm = get_llm(temperature=0.3, model_name=model_name)
                elif provider == "groq":
                    from app.services.groq_service import get_groq_llm

                    llm = get_groq_llm(temperature=0.3, model_name=model_name)  # type: ignore[assignment]
                else:
                    from app.services.gemini_service import get_llm

                    llm = get_llm(temperature=0.3, model_name=model_name)

                # Bind tools
                llm_with_tools = llm.bind_tools(self.tools)

                # Invoke
                logger.debug(f"Invoking {provider} LLM with model: {model_name}")
                response = llm_with_tools.invoke(messages)
                return cast(AIMessage, response)
            except Exception as e:
                logger.warning(f"⚠️ {provider} model {model_name} failed: {e}")
                last_error = e
                continue

        # If all models in current provider failed, try cross-provider fallback
        logger.warning(f"All {provider} models failed, attempting cross-provider fallback")
        try:
            response = invoke_with_fallback_provider(messages)
            # Bind tools to response if needed
            return response
        except Exception as e:
            logger.error(f"Cross-provider fallback also failed: {e}")
            last_error = e

        # If everything failed
        error_msg = f"All models and providers failed. Last error: {last_error}"
        logger.error(f"❌ {error_msg}")
        if last_error:
            raise last_error
        raise LLMServiceError(error_msg)

    @traceable(run_type="chain", name="process_message")
    def process_message(self, session_id: str, user_message: str) -> str:
        """
        Process a user message and return assistant response

        Args:
            session_id: Unique session identifier
            user_message: User's input message

        Returns:
            Assistant's response as a string
        """
        try:
            logger.info(f"🔵 Processing message for session {session_id}")
            logger.debug(f"User message: {user_message[:100]}...")

            # 🌍 Detect user's language
            detected_lang = detect_language(user_message)
            lang_instruction = get_language_instruction(detected_lang)
            logger.info(f"🌍 Detected language: {detected_lang}")

            # Add user message to memory
            self.memory_service.add_message(session_id, "user", user_message)

            # Get conversation history
            history = self.memory_service.get_history(session_id)
            logger.debug(f"Retrieved {len(history)} messages from history")

            # Retrieve context from vector store
            logger.info("📚 Retrieving context from vector store...")
            context_docs = self.vector_service.similarity_search(user_message, k=3)
            context = "\n\n".join([doc.page_content for doc in context_docs])
            logger.debug(f"Retrieved {len(context_docs)} context documents ({len(context)} chars)")

            # Build messages for LLM with language instruction
            system_prompt = get_system_prompt(context)
            system_prompt_with_lang = f"{system_prompt}\n\n{lang_instruction}"
            messages: list[BaseMessage] = [SystemMessage(content=system_prompt_with_lang)]

            # Add conversation history (convert BaseMessage to proper format)
            messages.extend(history)

            logger.info("💬 Invoking LLM with tool support...")
            logger.debug(f"Total messages in context: {len(messages)}")

            # Invoke LLM
            response = self._invoke_with_fallback(messages)
            logger.info(f"✅ LLM responded. Has tool calls: {bool(response.tool_calls)}")

            # Check if LLM wants to use tools
            if response.tool_calls:
                logger.info(f"🔧 LLM requested {len(response.tool_calls)} tool calls")

                # Add AI message with tool calls to messages
                messages.append(cast(BaseMessage, response))

                # Execute each tool call
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    logger.info(f"⚙️ Executing tool: {tool_name} with args: {tool_args}")

                    # Find and execute the tool
                    tool_output = None
                    for tool in self.tools:
                        if hasattr(tool, "name") and tool.name == tool_name:
                            try:
                                if hasattr(tool, "invoke"):
                                    tool_output = tool.invoke(tool_args)
                                    logger.info(f"✅ Tool {tool_name} executed successfully")
                                    logger.debug(f"Tool output: {str(tool_output)[:200]}...")
                            except Exception as e:
                                logger.error(f"❌ Tool {tool_name} failed: {str(e)}")
                                tool_output = f"Error executing tool: {str(e)}"
                            break

                    # Add tool result to messages
                    messages.append(
                        ToolMessage(content=str(tool_output), tool_call_id=tool_call["id"])
                    )

                # Get final response from LLM with tool results
                logger.info("💬 Getting final response from LLM after tool execution...")
                final_response = self._invoke_with_fallback(messages)
                assistant_response = final_response.content
                logger.info("✅ Final response generated successfully")
            else:
                # No tools needed, use direct response
                assistant_response = response.content
                logger.info("✅ Direct response (no tools used)")

            # Add assistant response to memory
            # Ensure assistant_response is a string
            assistant_response_str = (
                assistant_response
                if isinstance(assistant_response, str)
                else str(assistant_response)
            )
            self.memory_service.add_message(session_id, "assistant", assistant_response_str)
            logger.debug(f"Assistant response: {assistant_response_str[:100]}...")

            logger.info(f"🎉 Message processed successfully for session {session_id}")
            # Return the already-converted string
            return assistant_response_str

        except Exception as e:
            logger.error(f"❌ Error processing message: {str(e)}", exc_info=True)
            raise

    @traceable(run_type="chain", name="process_message_stream")
    async def process_message_stream(self, session_id: str, user_message: str):
        """
        Process a user message and stream assistant response in chunks.
        Handles tool calls properly by executing them and streaming final results.
        """
        try:
            logger.info(f"🔵 Processing streaming message for session {session_id}")
            logger.debug(f"User message: {user_message[:100]}...")

            # 🌍 Detect user's language with session persistence
            session_lang = self._session_languages.get(session_id)
            detected_lang = detect_language(user_message, session_hint=session_lang)
            self._session_languages[session_id] = detected_lang
            lang_instruction = get_language_instruction(detected_lang)
            logger.info(f"🌍 Detected language: {detected_lang}")

            # Add user message to memory
            self.memory_service.add_message(session_id, "user", user_message)

            # Get conversation history
            history = self.memory_service.get_history(session_id)
            logger.debug(f"Retrieved {len(history)} messages from history")

            # Retrieve context from vector store
            logger.info("📚 Retrieving context from vector store...")
            context_docs = self.vector_service.similarity_search(user_message, k=3)
            context = "\n\n".join([doc.page_content for doc in context_docs])
            logger.debug(f"Retrieved {len(context_docs)} context documents ({len(context)} chars)")

            # Build messages for LLM with language instruction
            system_prompt = get_system_prompt(context)
            system_prompt_with_lang = f"{system_prompt}\n\n{lang_instruction}"
            messages: list[BaseMessage] = [SystemMessage(content=system_prompt_with_lang)]
            messages.extend(history)

            logger.info("💬 Starting streaming response...")

            # Get model pool based on provider
            provider = settings.LLM_PROVIDER
            logger.info(f"Using LLM provider for streaming: {provider}")

            if provider == "gemini":
                model_pool = settings.GEMINI_MODEL_POOL
            elif provider == "groq":
                model_pool = settings.GROQ_MODEL_POOL
            else:
                logger.warning(f"Unknown provider '{provider}', defaulting to Gemini")
                model_pool = settings.GEMINI_MODEL_POOL
                provider = "gemini"

            last_error = None
            full_response = ""
            tool_calls_collected: list = []

            for model_name in model_pool:
                try:
                    # Get LLM for specific model based on provider
                    if provider == "gemini":
                        llm = get_llm(temperature=0.3, model_name=model_name)
                    elif provider == "groq":
                        from app.services.groq_service import get_groq_llm

                        llm = get_groq_llm(temperature=0.3, model_name=model_name)  # type: ignore[assignment]
                    else:
                        llm = get_llm(temperature=0.3, model_name=model_name)

                    llm_with_tools = llm.bind_tools(self.tools)
                    logger.debug(f"Streaming with {provider} model: {model_name}")

                    # First pass: Stream initial response and collect tool calls
                    async for chunk in llm_with_tools.astream(messages):
                        # Extract content from chunk
                        if hasattr(chunk, "content") and chunk.content:
                            content = chunk.content
                            if isinstance(content, str):
                                full_response += content
                                yield content
                            elif isinstance(content, list):
                                content_str = " ".join(
                                    str(item) for item in content if isinstance(item, str)
                                )
                                full_response += content_str
                                yield content_str

                        # Collect tool calls (don't yield ugly message)
                        if hasattr(chunk, "tool_calls") and chunk.tool_calls:
                            tool_calls_collected.extend(chunk.tool_calls)
                            logger.info(f"🔧 Collected {len(chunk.tool_calls)} tool calls")

                    # If we have tool calls, execute them and get final response
                    if tool_calls_collected:
                        logger.info(f"🔧 Executing {len(tool_calls_collected)} tool calls...")

                        # Yield a nice status indicator
                        yield "\n\n🔍 *Searching flights...*\n\n"

                        # Build tool response messages
                        from langchain.schema import AIMessage
                        from langchain_core.messages import ToolMessage

                        # Create AI message with tool calls
                        ai_message = AIMessage(
                            content=full_response, tool_calls=tool_calls_collected
                        )
                        messages.append(cast(BaseMessage, ai_message))

                        # Execute each tool
                        for tool_call in tool_calls_collected:
                            tool_name = tool_call.get("name", "")
                            tool_args = tool_call.get("args", {})
                            tool_id = tool_call.get("id", "")

                            logger.info(f"⚙️ Executing tool: {tool_name}")
                            tool_output = None

                            for tool in self.tools:
                                if hasattr(tool, "name") and tool.name == tool_name:
                                    try:
                                        # Use ainvoke for async tools
                                        if hasattr(tool, "ainvoke"):
                                            tool_output = await tool.ainvoke(tool_args)
                                        elif hasattr(tool, "invoke"):
                                            tool_output = tool.invoke(tool_args)
                                        logger.info(f"✅ Tool {tool_name} executed")
                                    except Exception as e:
                                        logger.error(f"❌ Tool {tool_name} failed: {e}")
                                        tool_output = f"Error: {str(e)}"
                                    break

                            # Add tool result
                            messages.append(
                                ToolMessage(
                                    content=str(tool_output) if tool_output else "No results found",
                                    tool_call_id=tool_id,
                                )
                            )

                        # Get final response with tool results
                        logger.info("💬 Getting final response with tool results...")
                        full_response = ""  # Reset for final response

                        async for chunk in llm_with_tools.astream(messages):
                            if hasattr(chunk, "content") and chunk.content:
                                content = chunk.content
                                if isinstance(content, str):
                                    full_response += content
                                    yield content
                                elif isinstance(content, list):
                                    content_str = " ".join(
                                        str(item) for item in content if isinstance(item, str)
                                    )
                                    full_response += content_str
                                    yield content_str

                    logger.info(f"✅ Streaming completed with {provider} model: {model_name}")
                    break

                except Exception as e:
                    logger.warning(f"⚠️ Streaming failed with {provider} model {model_name}: {e}")
                    last_error = e
                    continue

            # If all models failed
            if not full_response:
                error_msg = f"All {provider} models failed. Last error: {last_error}"
                logger.error(f"❌ {error_msg}")
                yield "\n\nI apologize, but I'm experiencing technical difficulties. Please try again.\n\n"

            # Add complete response to memory
            if full_response:
                self.memory_service.add_message(session_id, "assistant", full_response)
                logger.info(f"🎉 Streaming message processed successfully for session {session_id}")

        except Exception as e:
            logger.error(f"❌ Error in streaming: {str(e)}", exc_info=True)
            yield "\n\nI apologize, but an error occurred. Please try again.\n\n"

    def clear_session(self, session_id: str) -> None:
        """Clear the conversation history for a session"""
        self.memory_service.clear_session(session_id)
        logger.info(f"Cleared session {session_id}")


# Singleton instance
_chat_service: ChatService | None = None


def get_chat_service() -> ChatService:
    """Get the global ChatService instance"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
