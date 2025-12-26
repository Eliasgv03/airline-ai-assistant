"""
Test script for LLM Service

This script tests the LLM service integration with Google Gemini.
Run with: poetry run python -m app.scripts.test_llm
"""

import sys

from langchain_core.messages import BaseMessage

from app.services.gemini_service import LLMServiceError, chat_complete, create_message
from app.utils.logger import setup_logging

# Setup logging
setup_logging()


def test_basic_completion():
    """Test basic LLM completion"""
    print("\n" + "=" * 60)
    print("TEST 1: Basic Completion")
    print("=" * 60)

    try:
        messages = [
            create_message("system", "You are a helpful assistant."),
            create_message("user", "Say 'Hello, World!' in a friendly way."),
        ]

        response = chat_complete(messages, temperature=0.3)

        print("✅ Success!")
        print(f"Response: {response}")
        return True

    except LLMServiceError as e:
        print(f"❌ LLM Service Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False


def test_air_india_persona():
    """Test Air India persona response"""
    print("\n" + "=" * 60)
    print("TEST 2: Air India Persona")
    print("=" * 60)

    try:
        messages = [
            create_message(
                "system",
                "You are Air India's virtual assistant. Be professional and helpful.",
            ),
            create_message("user", "What can you help me with?"),
        ]

        response = chat_complete(messages, temperature=0.3)

        print("✅ Success!")
        print(f"Response: {response}")
        return True

    except LLMServiceError as e:
        print(f"❌ LLM Service Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False


def test_temperature_variation():
    """Test different temperature settings"""
    print("\n" + "=" * 60)
    print("TEST 3: Temperature Variation")
    print("=" * 60)

    try:
        messages = [
            create_message("system", "You are a creative writer."),
            create_message("user", "Write a one-sentence tagline for Air India."),
        ]

        print("\n📊 Testing different temperatures:")

        # Low temperature (deterministic)
        print("\n🔹 Temperature 0.0 (deterministic):")
        response_low = chat_complete(messages, temperature=0.0)
        print(f"   {response_low}")

        # Medium temperature (balanced)
        print("\n🔹 Temperature 0.5 (balanced):")
        response_med = chat_complete(messages, temperature=0.5)
        print(f"   {response_med}")

        # High temperature (creative)
        print("\n🔹 Temperature 1.0 (creative):")
        response_high = chat_complete(messages, temperature=1.0)
        print(f"   {response_high}")

        print("\n✅ All temperature tests passed!")
        return True

    except LLMServiceError as e:
        print(f"❌ LLM Service Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False


def test_error_handling():
    """Test error handling with invalid configuration"""
    print("\n" + "=" * 60)
    print("TEST 4: Error Handling")
    print("=" * 60)

    try:
        # Test with empty messages (should work but might give unexpected response)
        messages: list[BaseMessage] = []
        response = chat_complete(messages, temperature=0.3)
        print(f"⚠️  Empty messages handled: {response[:50]}...")
        return True

    except LLMServiceError as e:
        print(f"✅ Error handled correctly: {e}")
        return True
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🚀 LLM SERVICE TEST SUITE")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Basic Completion", test_basic_completion()))
    results.append(("Air India Persona", test_air_india_persona()))
    results.append(("Temperature Variation", test_temperature_variation()))
    results.append(("Error Handling", test_error_handling()))

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
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
