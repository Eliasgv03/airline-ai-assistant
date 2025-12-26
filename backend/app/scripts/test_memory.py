"""
Test script for Memory Service

This script tests the conversation memory service functionality.
Run with: poetry run python -m app.scripts.test_memory
"""

import time

from app.services.memory_service import get_memory_service
from app.utils.logger import setup_logging

# Setup logging
setup_logging()


def test_basic_memory():
    """Test basic memory operations"""
    print("\n" + "=" * 60)
    print("TEST 1: Basic Memory Operations")
    print("=" * 60)

    try:
        memory_service = get_memory_service()
        session_id = "test-session-1"

        # Add messages
        memory_service.add_message(session_id, "user", "Hello, I need help with baggage")
        memory_service.add_message(
            session_id, "assistant", "I'd be happy to help with baggage information!"
        )
        memory_service.add_message(session_id, "user", "What's the limit for international?")

        # Get history
        history = memory_service.get_history(session_id)

        print(f"✅ Session created: {session_id}")
        print(f"✅ Messages stored: {len(history)}")
        print("\n📝 Conversation history:")
        for i, msg in enumerate(history, 1):
            role = "User" if msg.type == "human" else "Assistant"
            print(f"   {i}. {role}: {msg.content[:50]}...")

        assert len(history) == 3, f"Expected 3 messages, got {len(history)}"
        print("\n✅ Test passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_multiple_sessions():
    """Test multiple concurrent sessions"""
    print("\n" + "=" * 60)
    print("TEST 2: Multiple Sessions")
    print("=" * 60)

    try:
        memory_service = get_memory_service()

        # Create multiple sessions
        sessions = {
            "user-alice": [
                ("user", "I want to fly to Delhi"),
                ("assistant", "Great! When would you like to travel?"),
            ],
            "user-bob": [
                ("user", "Check-in help needed"),
                ("assistant", "I can help you with check-in!"),
            ],
            "user-charlie": [
                ("user", "Baggage allowance?"),
                ("assistant", "Let me explain the baggage policy."),
            ],
        }

        # Add messages to each session
        for session_id, messages in sessions.items():
            for role, content in messages:
                memory_service.add_message(session_id, role, content)

        # Verify each session has correct history
        print(f"\n📊 Active sessions: {memory_service.get_session_count()}")

        for session_id in sessions.keys():
            history = memory_service.get_history(session_id)
            print(f"   • {session_id}: {len(history)} messages")
            assert len(history) == 2, f"Expected 2 messages for {session_id}"

        print("\n✅ All sessions isolated correctly!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_session_persistence():
    """Test that sessions persist across multiple accesses"""
    print("\n" + "=" * 60)
    print("TEST 3: Session Persistence")
    print("=" * 60)

    try:
        memory_service = get_memory_service()
        session_id = "persistent-session"

        # First interaction
        memory_service.add_message(session_id, "user", "First message")
        memory_service.add_message(session_id, "assistant", "First response")

        # Get history
        history1 = memory_service.get_history(session_id)
        print(f"✅ After first interaction: {len(history1)} messages")

        # Second interaction (should remember previous)
        memory_service.add_message(session_id, "user", "Second message")
        memory_service.add_message(session_id, "assistant", "Second response")

        # Get updated history
        history2 = memory_service.get_history(session_id)
        print(f"✅ After second interaction: {len(history2)} messages")

        assert len(history2) == 4, f"Expected 4 messages, got {len(history2)}"
        print("\n✅ Session persisted correctly!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_clear_session():
    """Test clearing a session"""
    print("\n" + "=" * 60)
    print("TEST 4: Clear Session")
    print("=" * 60)

    try:
        memory_service = get_memory_service()
        session_id = "temp-session"

        # Add messages
        memory_service.add_message(session_id, "user", "Temporary message")
        memory_service.add_message(session_id, "assistant", "Temporary response")

        history_before = memory_service.get_history(session_id)
        print(f"✅ Before clear: {len(history_before)} messages")

        # Clear session
        memory_service.clear_session(session_id)

        history_after = memory_service.get_history(session_id)
        print(f"✅ After clear: {len(history_after)} messages")

        assert len(history_after) == 0, "Expected 0 messages after clear"
        print("\n✅ Session cleared successfully!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_ttl_cleanup():
    """Test TTL-based session cleanup"""
    print("\n" + "=" * 60)
    print("TEST 5: TTL Cleanup (Fast Test)")
    print("=" * 60)

    try:
        # Create memory service with very short TTL (1 second for testing)
        from app.services.memory_service import MemoryService

        memory_service = MemoryService(ttl_minutes=0.016)  # ~1 second (0.016 minutes ≈ 1 second)

        session_id = "ttl-test-session"

        # Add message
        memory_service.add_message(session_id, "user", "This will expire")
        print(f"✅ Session created: {session_id}")
        print(f"   Active sessions: {memory_service.get_session_count()}")

        # Wait for TTL to expire
        print("⏳ Waiting 2 seconds for TTL expiration...")
        time.sleep(2)

        # Trigger cleanup by accessing memory
        memory_service.get_or_create_memory("trigger-cleanup")

        # Check if old session was cleaned up
        session_count = memory_service.get_session_count()
        print(f"   Active sessions after cleanup: {session_count}")

        # Note: session_count should be 1 (only trigger-cleanup session)
        # The ttl-test-session should have been cleaned up
        assert session_count == 1, f"Expected 1 session after cleanup, got {session_count}"

        print("\n✅ TTL cleanup working correctly!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🚀 MEMORY SERVICE TEST SUITE")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Basic Memory Operations", test_basic_memory()))
    results.append(("Multiple Sessions", test_multiple_sessions()))
    results.append(("Session Persistence", test_session_persistence()))
    results.append(("Clear Session", test_clear_session()))
    results.append(("TTL Cleanup", test_ttl_cleanup()))

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\n🎯 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    exit(main())
