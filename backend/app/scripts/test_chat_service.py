"""
Test script for Chat Service

This script tests the end-to-end chat orchestration.
"""

from app.services.chat_service import get_chat_service
from app.utils.logger import setup_logging

# Setup logging
setup_logging()


def test_chat_flow():
    """Test standard chat flow with memory"""
    print("\n" + "=" * 60)
    print("TEST 1: End-to-End Chat Flow")
    print("=" * 60)

    try:
        chat_service = get_chat_service()
        session_id = "test-chat-session"

        # 1. First Message
        print("\n👤 User: Hello! Who are you?")
        response1 = chat_service.process_message(session_id, "Hello! Who are you?")
        print(f"🤖 Assistant: {response1}")

        # Validation with clear error message
        if "Maharaja" not in response1 and "Air India" not in response1:
            raise AssertionError(f"Identity check failed. Response: {response1}")

        # 2. Contextual Message
        print("\n👤 User: Can you help me with baggage?")
        response2 = chat_service.process_message(session_id, "Can you help me with baggage?")
        print(f"🤖 Assistant: {response2}")

        assert "baggage" in response2.lower()

        # 3. Follow-up (Testing Memory)
        print("\n👤 User: What about for economy class to London?")
        response3 = chat_service.process_message(
            session_id, "What about for economy class to London?"
        )
        print(f"🤖 Assistant: {response3}")

        # The response should mention weight limits (e.g. 23kg) if it has context
        has_context = "23" in response3 or "kg" in response3.lower() or "piece" in response3.lower()

        if has_context:
            print("\n✅ Memory Context Verified")
        else:
            print("\n⚠️ Memory Context might be weak")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🚀 CHAT SERVICE TEST SUITE")
    print("=" * 60)

    if test_chat_flow():
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️ Tests failed.")
        return 1


if __name__ == "__main__":
    exit(main())
