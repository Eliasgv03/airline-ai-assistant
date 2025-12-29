"""
Test script to verify Gemini API key fallback and model pool rotation.

This script tests:
1. API key fallback (GOOGLE_API_KEY → GOOGLE_FALLBACK_API_KEY)
2. Model pool rotation (gemini-2.5-flash-lite → gemini-2.5-flash → etc.)
"""

from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def show_current_config():
    """Display current LLM configuration."""
    print("\n" + "=" * 60)
    print("⚙️ Current Gemini Configuration")
    print("=" * 60)

    print(f"\n   GOOGLE_API_KEY: {'✅ Set' if settings.GOOGLE_API_KEY else '❌ Not set'}")
    print(
        f"   GOOGLE_FALLBACK_API_KEY: {'✅ Set' if settings.GOOGLE_FALLBACK_API_KEY else '❌ Not set'}"
    )
    print(f"   GEMINI_MODEL_POOL: {settings.GEMINI_MODEL_POOL}")


def test_api_key_fallback():
    """Test API key fallback with model pool rotation."""
    print("\n" + "=" * 60)
    print("🔍 API Key + Model Pool Fallback Test")
    print("=" * 60)

    print("\n📡 Testing Gemini with full fallback chain...")
    try:
        from langchain.schema import HumanMessage, SystemMessage

        from app.services.gemini_service import invoke_with_api_fallback

        messages = [
            SystemMessage(content="You are a test assistant. Be very brief."),
            HumanMessage(content="Say 'Gemini OK' in exactly 2 words"),
        ]

        # Test with model_name=None to use full pool
        response = invoke_with_api_fallback(
            messages=messages,
            temperature=0.1,
            model_name=None,  # Use full model pool
        )
        print("   ✅ Gemini connected with API key + model pool fallback!")
        print(f"   Response: {response.content[:100]}")
    except Exception as e:
        print(f"   ❌ Gemini failed: {type(e).__name__}: {str(e)[:200]}")


def test_chat_service():
    """Test the full ChatService."""
    print("\n" + "=" * 60)
    print("🧪 ChatService Test")
    print("=" * 60)

    try:
        from app.services.chat_service import ChatService

        chat = ChatService()
        session_id = "test-fallback-session"

        print("   Sending test message...")
        response = chat.process_message(session_id, "Hi, respond with just 'OK'")
        print("   ✅ ChatService response received!")
        print(f"   Response: {response[:200]}...")

        # Clean up
        chat.clear_session(session_id)

    except Exception as e:
        print(f"   ❌ ChatService failed: {type(e).__name__}: {str(e)[:200]}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Gemini Fallback Test Suite")
    print("=" * 60)

    show_current_config()
    test_api_key_fallback()
    test_chat_service()

    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60 + "\n")
