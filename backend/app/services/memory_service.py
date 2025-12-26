"""
Memory Service - Session-based Conversation Memory

This service manages conversation history for each user session.
It stores messages in-memory and provides TTL-based cleanup.
"""

from datetime import datetime, timedelta
import logging
from typing import Any, cast

from langchain.memory import ConversationBufferMemory
from langchain_core.messages import BaseMessage

logger = logging.getLogger(__name__)


class MemoryService:
    """
    Manages conversation memory for multiple sessions.

    Each session has its own conversation history stored in-memory.
    Old sessions are automatically cleaned up based on TTL.
    """

    def __init__(self, ttl_minutes: int = 60):
        """
        Initialize the memory service.

        Args:
            ttl_minutes: Time-to-live for sessions in minutes (default: 60)
        """
        self._sessions: dict[str, dict[str, Any]] = {}
        self._ttl_minutes = ttl_minutes
        logger.info(f"Memory service initialized with TTL={ttl_minutes} minutes")

    def get_or_create_memory(self, session_id: str) -> ConversationBufferMemory:
        """
        Get existing memory for a session or create a new one.

        Args:
            session_id: Unique session identifier

        Returns:
            ConversationBufferMemory instance for the session
        """
        # Clean up old sessions first
        self._cleanup_old_sessions()

        # Get or create session
        if session_id not in self._sessions:
            logger.info(f"Creating new memory for session: {session_id}")
            self._sessions[session_id] = {
                "memory": ConversationBufferMemory(return_messages=True),
                "created_at": datetime.now(),
                "last_accessed": datetime.now(),
            }
        else:
            # Update last accessed time
            self._sessions[session_id]["last_accessed"] = datetime.now()

        return cast(ConversationBufferMemory, self._sessions[session_id]["memory"])

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        Add a message to the session history.

        Args:
            session_id: Unique session identifier
            role: Message role ('user' or 'assistant')
            content: Message content

        Raises:
            ValueError: If role is invalid
        """
        memory = self.get_or_create_memory(session_id)

        if role == "user":
            memory.chat_memory.add_user_message(content)
            logger.debug(f"Added user message to session {session_id}")
        elif role == "assistant":
            memory.chat_memory.add_ai_message(content)
            logger.debug(f"Added assistant message to session {session_id}")
        else:
            raise ValueError(f"Invalid role: {role}. Must be 'user' or 'assistant'")

    def get_history(self, session_id: str) -> list[BaseMessage]:
        """
        Get conversation history for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            List of messages in chronological order
        """
        if session_id not in self._sessions:
            logger.debug(f"No history found for session {session_id}")
            return []

        memory = self._sessions[session_id]["memory"]
        messages = memory.chat_memory.messages

        logger.debug(f"Retrieved {len(messages)} messages for session {session_id}")
        return cast(list[BaseMessage], messages)

    def clear_session(self, session_id: str) -> None:
        """
        Clear all messages for a session.

        Args:
            session_id: Unique session identifier
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Cleared session: {session_id}")
        else:
            logger.warning(f"Attempted to clear non-existent session: {session_id}")

    def get_session_count(self) -> int:
        """
        Get the number of active sessions.

        Returns:
            Number of active sessions
        """
        return len(self._sessions)

    def _cleanup_old_sessions(self) -> None:
        """
        Remove sessions that haven't been accessed within TTL.

        This is called automatically on each get_or_create_memory call.
        """
        now = datetime.now()
        ttl_delta = timedelta(minutes=self._ttl_minutes)

        sessions_to_remove = []

        for session_id, session_data in self._sessions.items():
            last_accessed = session_data["last_accessed"]
            age = now - last_accessed

            if age > ttl_delta:
                sessions_to_remove.append(session_id)

        # Remove old sessions
        for session_id in sessions_to_remove:
            del self._sessions[session_id]
            logger.info(f"Cleaned up expired session: {session_id}")

        if sessions_to_remove:
            logger.info(f"Cleaned up {len(sessions_to_remove)} expired sessions")


# Global memory service instance
_memory_service: MemoryService | None = None


def get_memory_service(ttl_minutes: int = 60) -> MemoryService:
    """
    Get the global memory service instance (singleton).

    Args:
        ttl_minutes: TTL for sessions (only used on first call)

    Returns:
        MemoryService instance
    """
    global _memory_service

    if _memory_service is None:
        _memory_service = MemoryService(ttl_minutes=ttl_minutes)
        logger.info("Global memory service created")

    return _memory_service
