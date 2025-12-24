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
from app.services.vector_service import VectorService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChatService:
    """
    Orchestrates the chat flow for the Air India Assistant.
    """

    def __init__(self):
        """Initialize the chat service."""
        self.memory_service = get_memory_service()
        self.vector_service = VectorService()
        logger.info("ChatService initialized with RAG support")

    def process_message(self, session_id: str, user_message: str) -> str:
        """
        Process a user message and generate a response with RAG context.
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

            # 4. Construct messages for LLM
            system_prompt = get_system_prompt()

            # Inject RAG context into instructions
            full_instructions = f"{system_prompt}\n{context_text}"

            # NOTE: Using 'user' role for system prompt to force finding identity in some models
            messages = [
                create_message(
                    "user", f"SYSTEM INSTRUCTIONS:\n{full_instructions}\n\nCONFIRM YOU UNDERSTAND."
                ),
                create_message(
                    "assistant",
                    "I understand. I am Maharaja Assistant, Air India's virtual assistant. I have access to the provided policies and history. I am ready to help.",
                ),
                *history,
            ]

            # 5. Generate response
            response_text = chat_complete(messages, temperature=0.3)

            # 6. Add assistant response to history
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
