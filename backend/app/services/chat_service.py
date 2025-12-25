"""
Chat Service - Orchestrates conversation flow with RAG and LLM

This service integrates memory, vector search, and LLM to provide contextual responses.
"""

import logging

from langchain.schema import AIMessage, SystemMessage
from langchain_core.messages import ToolMessage

from app.core.config import get_settings
from app.prompts.system_prompts import get_system_prompt
from app.services.llm_service import LLMServiceError, get_llm
from app.services.memory_service import get_memory_service
from app.services.vector_service import VectorService
from app.tools import ALL_TOOLS

logger = logging.getLogger(__name__)
settings = get_settings()


class ChatService:
    """Service for handling chat interactions with RAG and tool support"""

    def __init__(self):
        self.memory_service = get_memory_service()
        self.vector_service = VectorService()
        self.tools = ALL_TOOLS
        logger.info(f"ChatService initialized with RAG support and {len(self.tools)} tools")

    def _invoke_with_fallback(self, messages) -> AIMessage:
        """
        Invoke LLM with automatic fallback to other models in the pool.
        """
        last_error = None
        for model_name in settings.GEMINI_MODEL_POOL:
            try:
                # Get LLM for specific model
                llm = get_llm(temperature=0.3, model_name=model_name)

                # Bind tools
                llm_with_tools = llm.bind_tools(self.tools)

                # Invoke
                logger.debug(f"Invoking LLM with model: {model_name}")
                return llm_with_tools.invoke(messages)
            except Exception as e:
                logger.warning(f"⚠️ Model {model_name} failed: {e}")
                last_error = e
                continue

        # If all execution attempts fail
        error_msg = f"All models failed. Last error: {last_error}"
        logger.error(f"❌ {error_msg}")
        if last_error:
            raise last_error
        raise LLMServiceError(error_msg)

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

            # Build messages for LLM
            system_prompt = get_system_prompt(context)
            messages = [SystemMessage(content=system_prompt)]

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
                messages.append(response)

                # Execute each tool call
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    logger.info(f"⚙️ Executing tool: {tool_name} with args: {tool_args}")

                    # Find and execute the tool
                    tool_output = None
                    for tool in self.tools:
                        if tool.name == tool_name:
                            try:
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
            self.memory_service.add_message(session_id, "assistant", assistant_response)
            logger.debug(f"Assistant response: {assistant_response[:100]}...")

            logger.info(f"🎉 Message processed successfully for session {session_id}")
            return assistant_response

        except Exception as e:
            logger.error(f"❌ Error processing message: {str(e)}", exc_info=True)
            raise

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
