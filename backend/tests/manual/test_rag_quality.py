"""
RAG Quality Test

Verifies that the ChatService can answer policy questions using the ingested knowledge base.
Usage: poetry run python -m app.scripts.test_rag_quality
"""

import asyncio
import sys

# Windows asyncio fix
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.services.chat_service import get_chat_service
from app.utils.logger import setup_logging

setup_logging()


async def run_tests():
    chat_service = get_chat_service()
    session_id = "quality-test-session"

    queries = [
        "What is the baggage allowance for domestic economy class?",
        "Can I bring a power bank in my checked luggage?",
        "How many hours before an international flight does web check-in close?",
        "What are the dimensions for cabin baggage?",
    ]

    print("\n" + "=" * 50)
    print("STARTING RAG QUALITY TESTS")
    print("=" * 50 + "\n")

    for query in queries:
        print(f"USER: {query}")
        response = chat_service.process_message(session_id, query)
        print(f"ASSISTANT: {response}")
        print("-" * 30)


if __name__ == "__main__":
    asyncio.run(run_tests())
