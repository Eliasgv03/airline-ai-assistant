"""
Test script to verify round-robin API key and model rotation.

Sends 6 messages and shows which API key + model was used for each.
"""

import logging
from pathlib import Path
import sys

# Add parent to path - must be before local imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configure logging to show rotation logs
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",  # Simple format to see rotation clearly
)

# Suppress noisy loggers
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# Local imports after path setup  # noqa: E402
from app.core.config import get_settings  # noqa: E402
from app.services.gemini_service import get_all_combinations  # noqa: E402

settings = get_settings()


def test_round_robin():
    """Send 6 messages and show the round-robin rotation."""
    from langchain.schema import HumanMessage, SystemMessage

    from app.services.gemini_service import invoke_with_api_fallback

    print("\n" + "=" * 70)
    print("🔄 ROUND-ROBIN ROTATION TEST")
    print("=" * 70)

    combinations = get_all_combinations()
    print(f"\n📋 Total combinations: {len(combinations)}")
    for i, (_model, _, _key_name, combo_id) in enumerate(combinations):
        print(f"   {i + 1}. {combo_id}")

    print("\n" + "=" * 70)
    print("� Sending 6 messages (watch the rotation!)")
    print("=" * 70)

    for i in range(1, 7):
        print(f"\n{'─' * 70}")
        print(f"📤 MESSAGE {i}/6:")
        print("─" * 70)

        messages = [
            SystemMessage(content="Reply with just 'OK' and the number I give you."),
            HumanMessage(content=f"{i}"),
        ]

        try:
            response = invoke_with_api_fallback(
                messages=messages,
                temperature=0.1,
            )
            print(f"📥 Response: {response.content}")
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {str(e)[:100]}")

    print("\n" + "=" * 70)
    print("✅ Test completed! Check the logs above to see the rotation pattern.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    test_round_robin()
