"""
Chat Service - Core Orchestrator with Tool Support

This service orchestrates the chat interaction by combining:
1. Session-based Memory (Context)
2. System Prompts (Persona)
3. RAG (Retrieval-Augmented Generation)
4. Tools (Flight search, etc.)
5. LLM Execution (Generation)

It serves as the main entry point for the chat API.
"""


from app.prompts.system_prompts import get_system_prompt
from app.services.llm_service import create_message, get_llm
from app.services.memory_service import get_memory_service
from app.services.vector_service import VectorService
from app.tools import ALL_TOOLS
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChatService:
    """
    Orchestrates the chat flow for the Air India Assistant with tool support.
    """

    def __init__(self):
        """Initialize the chat service with tools."""
        self.memory_service = get_memory_service()
        self.vector_service = VectorService()
        self.tools = ALL_TOOLS
        logger.info(f"ChatService initialized with RAG support and {len(self.tools)} tools")

    def process_message(self, session_id: str, user_message: str) -> str:
        """
        Process a user message and generate a response with RAG context and tool support.
        """
        logger.info(f"Processing message for session {session_id}")

        try:
            # 1. Add user message to history
            self.memory_service.add_message(session_id, "user", user_message)

            # 2. Get conversation history
            history = self.memory_service.get_history(session_id)

            # 3. RAG: Retrieve relevant context
            logger.info("Retrieving context from vector store...")
            relevant_docs = self.vector_service.similarity_search(user_message, k=3)

            context_text = ""
            if relevant_docs:
                context_text = "\n\nRELEVANT AIR INDIA POLICIES:\n"
                for doc in relevant_docs:
                    context_text += (
                        f"--- FROM DOCUMENT: {doc.metadata.get('source', 'Unknown')} ---\n"
                    )
                    context_text += f"{doc.page_content}\n\n"

            # 4. Get LLM with tools bound
            llm = get_llm(temperature=0.3)
            llm_with_tools = llm.bind_tools(self.tools)

            # 5. Construct messages for LLM
            system_prompt = get_system_prompt()

            # Inject RAG context and tool instructions
            full_instructions = f"""{system_prompt}

{context_text}

## AVAILABLE TOOLS

You have access to the following tools:
- search_flights: Search for Air India flights between two cities
- get_flight_details: Get details about a specific flight by flight number

Use these tools when users ask about flights, schedules, or availability.
Always provide helpful, natural responses based on the tool results.
"""

            # Build message history
            messages = [
                create_message(
                    "user", f"SYSTEM INSTRUCTIONS:\n{full_instructions}\n\nCONFIRM YOU UNDERSTAND."
                ),
                create_message(
                    "assistant",
                    "I understand. I am Maharaja Assistant, Air India's virtual assistant. I have access to policies, flight search tools, and conversation history. I am ready to help.",
                ),
                *history,
            ]

            # 6. Invoke LLM (may call tools automatically)
            logger.info("Invoking LLM with tool support...")
            response = llm_with_tools.invoke(messages)

            # 7. Check if tools were called
            if hasattr(response, "tool_calls") and response.tool_calls:
                logger.info(f"LLM requested {len(response.tool_calls)} tool call(s)")

                # Execute tools and collect results
                tool_results = []
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")

                    # Find and execute the tool
                    tool_func = next((t for t in self.tools if t.name == tool_name), None)
                    if tool_func:
                        try:
                            result = tool_func.invoke(tool_args)
                            tool_results.append(result)
                            logger.info(f"Tool {tool_name} executed successfully")
                        except Exception as e:
                            logger.error(f"Error executing tool {tool_name}: {str(e)}")
                            tool_results.append(f"Error: {str(e)}")
                    else:
                        logger.warning(f"Tool {tool_name} not found")
                        tool_results.append(f"Tool {tool_name} not available")

                # 8. Generate final response with tool results
                tool_results_text = "\n\n".join(tool_results)
                final_messages = messages + [
                    create_message("assistant", f"[Tool Results]\n{tool_results_text}"),
                    create_message(
                        "user",
                        "Based on the tool results above, provide a natural, helpful response to the user.",
                    ),
                ]

                final_response = llm.invoke(final_messages)
                response_text = final_response.content

            else:
                # No tools called, use direct response
                response_text = response.content

            # 9. Add assistant response to history
            self.memory_service.add_message(session_id, "assistant", response_text)

            logger.info(f"Response generated for session {session_id}")
            return response_text

        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}")
            # In a real app, you might want to return a graceful error message to the user
            # For now, re-raise to be handled by the API layer error handlers
            raise

    def clear_session(self, session_id: str) -> None:
        """
        Clear the conversation history for a session.

        Args:
            session_id: Session ID to clear
        """
        self.memory_service.clear_session(session_id)
        logger.info(f"Cleared session {session_id}")


# Singleton instance
_chat_service: ChatService | None = None


def get_chat_service() -> ChatService:
    """Get the global ChatService instance."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
