"""
Chat Service - Orchestrates conversation flow with RAG and LLM

This service integrates memory, vector search, and LLM to provide contextual responses.
"""

import logging
from typing import cast

from langchain.schema import AIMessage, SystemMessage
from langchain_core.messages import BaseMessage, ToolMessage
from langsmith import traceable

from app.core.config import get_settings
from app.prompts.system_prompts import get_system_prompt
from app.services.language_service import detect_language, get_language_instruction
from app.services.llm_base import LLMServiceError
from app.services.llm_manager import llm_manager
from app.services.memory_service import get_memory_service
from app.services.vector_service import get_vector_service
from app.tools import ALL_TOOLS

logger = logging.getLogger(__name__)
settings = get_settings()


class ChatService:
    """Service for handling chat interactions with RAG and tool support"""

    def __init__(self):
        self.memory_service = get_memory_service()

        # Initialize VectorService (Google Embeddings API - instant, no model loading)
        self.vector_service = None
        self._rag_available = False

        try:
            self.vector_service = get_vector_service()
            self._rag_available = True
            logger.info("✅ ChatService initialized with RAG support")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize VectorService: {e} - continuing without RAG")

        self.tools = ALL_TOOLS
        self._session_languages: dict[str, str] = {}  # Track language per session
        logger.info(
            f"ChatService initialized with {len(self.tools)} tools (RAG: {self._rag_available})"
        )

    def _invoke_with_fallback(self, messages) -> AIMessage:
        """
        Invoke LLM with automatic fallback.

        Uses llm_manager which routes to the configured provider (Gemini, Groq, etc.)
        Gemini uses round-robin rotation across API keys and models.
        """
        logger.info(f"🤖 Invoking LLM via {llm_manager.provider_name}")

        try:
            response = llm_manager.invoke(
                messages=messages,
                temperature=0.3,
                model_name=None,  # Use rotation (Gemini) or default (others)
                tools=self.tools,
            )
            return response

        except LLMServiceError as e:
            logger.error(f"❌ LLM invocation failed: {e}")
            raise

    def _prepare_context(self, session_id: str, user_message: str) -> list[BaseMessage]:
        """
        Common setup for both sync and async chat processing.
        Handles language detection, memory update, RAG retrieval, and prompt construction.
        """
        logger.info(f"🔵 Preparing context for session {session_id}")
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

        # Retrieve context from vector store (if RAG is available)
        context = ""
        if self._rag_available and self.vector_service:
            logger.info("📚 Retrieving context from vector store...")
            context_docs = self.vector_service.similarity_search(user_message, k=3)
            context = "\n\n".join([doc.page_content for doc in context_docs])
            logger.debug(f"Retrieved {len(context_docs)} context documents ({len(context)} chars)")
        else:
            logger.info("📚 RAG not available - proceeding without knowledge base context")

        # Build messages for LLM with language instruction
        system_prompt = get_system_prompt(context)
        system_prompt_with_lang = f"{system_prompt}\n\n{lang_instruction}"
        messages: list[BaseMessage] = [SystemMessage(content=system_prompt_with_lang)]
        messages.extend(history)

        return messages

    @traceable(run_type="chain", name="process_message")
    def process_message(self, session_id: str, user_message: str) -> str:
        """
        Process a user message and return assistant response
        """
        try:
            # Shared setup
            messages = self._prepare_context(session_id, user_message)

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
            assistant_response_str = (
                assistant_response
                if isinstance(assistant_response, str)
                else str(assistant_response)
            )
            self.memory_service.add_message(session_id, "assistant", assistant_response_str)
            logger.debug(f"Assistant response: {assistant_response_str[:100]}...")

            logger.info(f"🎉 Message processed successfully for session {session_id}")
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
            # Shared setup
            messages = self._prepare_context(session_id, user_message)

            logger.info(f"💬 Starting streaming via {llm_manager.provider_name}...")

            full_response = ""
            tool_calls_collected: list = []

            try:
                # First pass: Stream initial response and collect tool calls
                async for chunk in llm_manager.astream(
                    messages=messages,
                    temperature=0.3,
                    tools=self.tools,
                ):
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

                    # Create AI message with tool calls
                    ai_message = AIMessage(content=full_response, tool_calls=tool_calls_collected)
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
                                    if hasattr(tool, "ainvoke"):
                                        tool_output = await tool.ainvoke(tool_args)
                                    elif hasattr(tool, "invoke"):
                                        tool_output = tool.invoke(tool_args)
                                    logger.info(f"✅ Tool {tool_name} executed")
                                except Exception as e:
                                    logger.error(f"❌ Tool {tool_name} failed: {e}")
                                    tool_output = f"Error: {str(e)}"
                                break

                        messages.append(
                            ToolMessage(
                                content=str(tool_output) if tool_output else "No results found",
                                tool_call_id=tool_id,
                            )
                        )

                    # Get final response with tool results
                    logger.info("💬 Getting final response with tool results...")
                    full_response = ""  # Reset for final response

                    async for chunk in llm_manager.astream(
                        messages=messages,
                        temperature=0.3,
                        tools=None,  # No tools for final response
                    ):
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

                logger.info(f"✅ Streaming completed via {llm_manager.provider_name}")

            except LLMServiceError as e:
                logger.error(f"❌ Streaming failed: {e}")
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
