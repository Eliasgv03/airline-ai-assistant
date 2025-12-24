"""
Test Flight Search Tool Integration

This script tests the flight search functionality via the chat service.
"""

from app.services.chat_service import get_chat_service
from app.utils.logger import setup_logging

# Setup logging
setup_logging()

# Test queries
TEST_QUERIES = [
    # Basic flight search
    "Find flights from Delhi to Mumbai",
    # Natural language
    "I want to fly from Mumbai to Bangalore tomorrow",
    # International flight
    "Show me flights to London from Delhi",
    # Specific flight details
    "Tell me about flight AI 865",
    # Mixed query (RAG + Tool)
    "What's the baggage allowance and show me flights to Goa from Mumbai",
    # Follow-up question (context)
    "What about the morning flights?",
]


def test_flight_search():
    """Test flight search tool integration"""
    chat_service = get_chat_service()
    session_id = "test_flight_search"

    print("=" * 80)
    print("TESTING FLIGHT SEARCH TOOL INTEGRATION")
    print("=" * 80)

    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(TEST_QUERIES)}")
        print(f"{'='*80}")
        print(f"USER: {query}")
        print(f"{'-'*80}")

        try:
            response = chat_service.process_message(session_id, query)
            print(f"ASSISTANT: {response}")
            print(f"{'='*80}")

        except Exception as e:
            print(f"ERROR: {str(e)}")
            print(f"{'='*80}")

    print("\n" + "=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_flight_search()
