"""
Test LangSmith Tracing Configuration

Verifies that LangSmith is properly configured and can trace LLM calls.
"""

# ruff: noqa: E402
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import get_settings


def test_langsmith_config():
    """Test LangSmith configuration"""
    settings = get_settings()

    print("=" * 80)
    print("🔍 LANGSMITH CONFIGURATION TEST")
    print("=" * 80)

    print("\n📋 Configuration:")
    print(f"  LANGSMITH_TRACING: {settings.LANGSMITH_TRACING}")
    print(f"  LANGSMITH_API_KEY: {'✅ Set' if settings.LANGSMITH_API_KEY else '❌ Not set'}")
    print(f"  LANGSMITH_PROJECT: {settings.LANGSMITH_PROJECT}")
    print(f"  LANGSMITH_ENDPOINT: {settings.LANGSMITH_ENDPOINT}")
    print(f"\n  Tracing Enabled: {'✅ Yes' if settings.is_tracing_enabled else '❌ No'}")

    if settings.is_tracing_enabled:
        print("\n✅ LangSmith is properly configured!")
        print(f"   View traces at: https://smith.langchain.com/o/{settings.LANGSMITH_PROJECT}")
        print("\n📊 What you'll see in LangSmith:")
        print("   - All LLM calls (Gemini and Groq)")
        print("   - Prompts and responses")
        print("   - Latency and token usage")
        print("   - Error traces")
        print("   - Custom metadata (session, language, provider)")
    else:
        print("\n⚠️ LangSmith is not enabled")
        print("   To enable:")
        print("   1. Set LANGSMITH_TRACING=true in .env")
        print("   2. Set LANGSMITH_API_KEY=your_key in .env")
        print("   3. Get your key from: https://smith.langchain.com")


if __name__ == "__main__":
    test_langsmith_config()
