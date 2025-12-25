"""
Quick test for language detection service
"""

# ruff: noqa: E402
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.language_service import (
    detect_language,
    get_language_instruction,
    get_language_name,
)


def test_language_detection():
    """Test language detection with various inputs"""
    print("=" * 80)
    print("🧪 TESTING LANGUAGE DETECTION")
    print("=" * 80)

    test_cases = [
        ("Hello, how are you?", "en"),
        ("Hola, ¿cómo estás?", "es"),
        ("नमस्ते, आप कैसे हैं?", "hi"),
        ("Bonjour, comment allez-vous?", "fr"),
        ("How much baggage can I bring?", "en"),
        ("¿Cuánto equipaje puedo llevar?", "es"),
        ("मुझे कितना सामान ले जाने की अनुमति है?", "hi"),
    ]

    print(f"\n📋 Testing {len(test_cases)} cases:\n")

    for text, expected_lang in test_cases:
        detected = detect_language(text)
        lang_name = get_language_name(detected)
        status = "✅" if detected == expected_lang else "⚠️"

        print(f"{status} Text: '{text[:50]}...'")
        print(f"   Expected: {expected_lang}, Detected: {detected} ({lang_name})")
        print()

    # Test language instruction
    print("=" * 80)
    print("📝 TESTING LANGUAGE INSTRUCTION GENERATION")
    print("=" * 80)

    for lang_code in ["en", "es", "hi"]:
        instruction = get_language_instruction(lang_code)
        print(f"\n🌍 Language: {get_language_name(lang_code)} ({lang_code})")
        print(f"Instruction preview: {instruction[:150]}...")
        print()


if __name__ == "__main__":
    test_language_detection()
