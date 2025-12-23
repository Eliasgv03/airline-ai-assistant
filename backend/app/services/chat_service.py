"""
Chat Service - Core Orchestrator

This service orchestrates the chat interaction by combining:
1. Session-based Memory (Context)
2. System Prompts (Persona)
3. LLM Execution (Generation)

It serves as the main entry point for the chat API.
"""


from app.prompts.system_prompts import get_system_prompt
from app.services.llm_service import chat_complete, create_message
from app.services.memory_service import get_memory_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChatService:
    """
    Orchestrates the chat flow for the Air India Assistant.
    """

    def __init__(self):
        """Initialize the chat service."""
        self.memory_service = get_memory_service()
        logger.info("ChatService initialized")

    def process_message(self, session_id: str, user_message: str) -> str:
        """
        Process a user message and generate a response.

        Flow:
        1. Retrieve/Create session memory
        2. Add user message to memory
        3. Construct full prompt (System Persona + History)
        4. Generate response via LLM
        5. Add response to memory
        6. Return response

        Args:
            session_id: Unique session identifier
            user_message: The user's input text

        Returns:
            The assistant's generated response
        """
        logger.info(f"Processing message for session {session_id}")

        try:
            # 1. Add user message to history
            self.memory_service.add_message(session_id, "user", user_message)

            # 2. Get conversation history
            history = self.memory_service.get_history(session_id)

            # 3. Construct messages for LLM
            # Start with the Unified System Prompt (Persona)
            system_prompt = get_system_prompt()

            # NOTE: Using 'user' role for system prompt to force finding identity in some models
            # that might ignore system instructions.
            messages = [
                create_message(
                    "user", f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\nCONFIRM YOU UNDERSTAND."
                ),
                create_message(
                    "assistant",
                    "I understand. I am Maharaja Assistant, Air India's virtual assistant. I am ready to help.",
                ),
                *history,  # Unpack the entire conversation history
            ]

            # 4. Generate response
            # Using moderate temperature for balance between creativity and accuracy
            response_text = chat_complete(messages, temperature=0.3)

            # 5. Add assistant response to history
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
