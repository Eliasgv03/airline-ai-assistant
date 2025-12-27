"""
RAG Single Test

Verifies that the ChatService can answer ONE policy question.
Usage: poetry run python -m app.scripts.test_rag_single
"""

import asyncio
import sys

# Windows asyncio fix
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.services.chat_service import get_chat_service
from app.utils.logger import setup_logging

setup_logging()


async def run_test():
    chat_service = get_chat_service()
    session_id = "single-test-session"

    query = "What is the baggage allowance for domestic economy class?"

    print(f"\nUSER: {query}")
    try:
        response = chat_service.process_message(session_id, query)
        print(f"ASSISTANT: {response}\n")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    asyncio.run(run_test())
