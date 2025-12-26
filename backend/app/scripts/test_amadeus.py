"""
Test Amadeus Flight API Integration

This script tests the flight search functionality with Amadeus API
and fallback to mock data.
"""

# ruff: noqa: E402
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.flight_service import get_flight_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def test_flight_search():
    """Test flight search with API and fallback"""
    print("=" * 80)
    print("🧪 TESTING FLIGHT SEARCH WITH AMADEUS API")
    print("=" * 80)

    flight_service = get_flight_service()

    # Test cases
    test_cases = [
        ("Delhi", "Mumbai", "tomorrow"),
        ("DEL", "BLR", "any"),
        ("Mumbai", "Dubai", "today"),
    ]

    for origin, destination, date in test_cases:
        print(f"\n{'=' * 80}")
        print(f"🔍 Test: {origin} → {destination} (date: {date})")
        print("=" * 80)

        try:
            flights = await flight_service.search_flights(
                origin=origin, destination=destination, date=date, max_results=3
            )

            if flights:
                print(f"\n✅ Found {len(flights)} flights:\n")
                for flight in flights:
                    print(flight_service.format_flight_for_display(flight))
                    print()
            else:
                print(f"\n❌ No flights found for {origin} → {destination}")

        except Exception as e:
            print(f"\n❌ Error: {e}")

    print("\n" + "=" * 80)
    print("✅ TESTING COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_flight_search())
