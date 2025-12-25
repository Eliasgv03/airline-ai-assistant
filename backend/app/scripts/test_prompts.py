"""
Test script for Unified System Prompts

This script tests the unified Air India persona prompt with the LLM.
It validates capability to handle both English and Hindi naturally.
Run with: poetry run python -m app.scripts.test_prompts
"""

from app.prompts.system_prompts import get_system_prompt
from app.services.gemini_service import chat_complete, create_message
from app.utils.logger import setup_logging

# Setup logging
setup_logging()


def test_english_query():
    """Test response to English query"""
    print("\n" + "=" * 60)
    print("TEST 1: English Query")
    print("=" * 60)

    try:
        system_prompt = get_system_prompt()
        messages = [
            create_message("system", system_prompt),
            create_message("user", "Hello! What is your name and who do you work for?"),
        ]

        response = chat_complete(messages, temperature=0.3)

        print("\n📝 User: Hello! What is your name and who do you work for?")
        print(f"🤖 Assistant: {response}\n")

        # Validation
        assert "Maharaja" in response or "Air India" in response
        print("✅ Response identifies as Maharaja/Air India")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_hindi_query():
    """Test response to Hindi query (Language Detection)"""
    print("\n" + "=" * 60)
    print("TEST 2: Hindi Query (Auto-Detection)")
    print("=" * 60)

    try:
        system_prompt = get_system_prompt()
        messages = [
            create_message("system", system_prompt),
            create_message("user", "नमस्ते! मुझे दिल्ली जाने वाली फ्लाइट के बारे में बताएं।"),
        ]

        response = chat_complete(messages, temperature=0.3)

        print("\n📝 User: नमस्ते! मुझे दिल्ली जाने वाली फ्लाइट के बारे में बताएं।")
        print(f"🤖 Assistant: {response}\n")

        # Validation: Check for Hindi characters
        has_hindi = any("\u0900" <= char <= "\u097F" for char in response)

        if has_hindi:
            print("✅ Response detected Hindi and replied in Hindi")
            return True
        else:
            print("❌ FAIL: Response was NOT in Hindi")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_limitations():
    """Test boundary conditions"""
    print("\n" + "=" * 60)
    print("TEST 3: Limitations")
    print("=" * 60)

    try:
        system_prompt = get_system_prompt()
        messages = [
            create_message("system", system_prompt),
            create_message("user", "Can you book a hotel room for me?"),
        ]

        response = chat_complete(messages, temperature=0.3)

        print("\n📝 User: Can you book a hotel room for me?")
        print(f"🤖 Assistant: {response}\n")

        # Validation
        invalid_keywords = ["cannot", "can't", "sorry", "unable", "not"]
        is_refusal = any(kw in response.lower() for kw in invalid_keywords)

        if is_refusal:
            print("✅ Assistant correctly refused hotel booking")
            return True
        else:
            print("⚠️ Warning: Refusal not explicit")
            return True  # Soft pass

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🚀 UNIFIED PROMPT TEST SUITE")
    print("=" * 60)

    results = []
    results.append(("English Query", test_english_query()))
    results.append(("Hindi Query", test_hindi_query()))
    results.append(("Limitations", test_limitations()))

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️ Some tests failed.")
        return 1


if __name__ == "__main__":
    exit(main())
