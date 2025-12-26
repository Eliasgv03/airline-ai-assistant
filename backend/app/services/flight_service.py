"""
Flight Search Service with Real API Integration

Provides flight search functionality with Amadeus API integration
and automatic fallback to mock data.
"""

import os

from app.models.flight import Flight
from app.services.amadeus_api import get_amadeus_api
from app.utils.logger import get_logger
from data.flight_data import FLIGHTS_DB, normalize_location

logger = get_logger(__name__)


class FlightService:
    """Service for searching flights with API integration and fallback"""

    def __init__(self):
        self.amadeus_api = get_amadeus_api()
        self.flights_db = FLIGHTS_DB
        self.use_real_api = os.getenv("USE_REAL_FLIGHT_API", "true").lower() == "true"

        logger.info(
            f"FlightService initialized: "
            f"Real API={'enabled' if self.use_real_api else 'disabled'}, "
            f"Mock flights={len(self.flights_db)}"
        )

    async def search_flights(
        self,
        origin: str,
        destination: str,
        date: str | None = None,
        max_results: int = 10,
    ) -> list[Flight]:
        """
        Search for flights with automatic API fallback

        Priority:
        1. Try real API (if enabled and configured)
        2. Fallback to mock data

        Args:
            origin: Origin city or airport code
            destination: Destination city or airport code
            date: Optional date filter
            max_results: Maximum number of results

        Returns:
            List of Flight objects
        """
        origin_code = normalize_location(origin)
        destination_code = normalize_location(destination)

        logger.info(f"🔍 Searching flights: {origin_code} → {destination_code}, date={date}")

        # Try real API first
        if self.use_real_api and self.amadeus_api.is_configured():
            try:
                logger.info("🌐 Attempting Amadeus API search...")
                flights = await self.amadeus_api.search_flights(
                    origin=origin_code,
                    destination=destination_code,
                    date=date,
                    max_results=max_results,
                )

                if flights:
                    logger.info(f"✅ Found {len(flights)} flights from Amadeus API")
                    return flights
                else:
                    logger.warning("⚠️ Amadeus API returned no flights, using mock data")

            except Exception as e:
                logger.error(f"❌ Amadeus API failed: {e}, falling back to mock data")

        # Fallback to mock data
        logger.info(f"📦 Using mock data for {origin_code} → {destination_code}")
        return self._search_mock_flights(origin_code, destination_code, max_results)

    def _search_mock_flights(
        self, origin: str, destination: str, max_results: int = 10
    ) -> list[Flight]:
        """
        Search mock flight data

        Args:
            origin: Origin airport code
            destination: Destination airport code
            max_results: Maximum results

        Returns:
            List of Flight objects
        """
        # Filter flights by route
        matching_flights = [
            flight
            for flight in self.flights_db
            if flight["origin"] == origin and flight["destination"] == destination
        ]

        if not matching_flights:
            logger.info(f"❌ No mock data for route {origin} → {destination}")
            return []

        # Sort by departure time
        matching_flights.sort(key=lambda f: f["departure_time"])

        # Limit results
        results = matching_flights[:max_results]

        # Convert to Flight objects
        flights = []
        for flight_data in results:
            flight = Flight(
                flight_number=flight_data["flight_number"],
                origin=flight_data["origin"],
                origin_city=flight_data["origin_city"],
                destination=flight_data["destination"],
                destination_city=flight_data["destination_city"],
                departure_time=flight_data["departure_time"],
                arrival_time=flight_data["arrival_time"],
                duration=flight_data["duration"],
                aircraft=flight_data["aircraft"],
                price_economy=flight_data["price_economy"],
                price_business=flight_data["price_business"],
                available_seats=9,  # Default
            )
            flights.append(flight)

        logger.info(f"📦 Found {len(flights)} mock flights")
        return flights

    def get_flight_by_number(self, flight_number: str) -> Flight | None:
        """
        Get flight details by flight number from mock data

        Args:
            flight_number: Flight number (e.g., "AI 865")

        Returns:
            Flight object or None
        """
        flight_number = flight_number.upper().strip()

        for flight_data in self.flights_db:
            if flight_data["flight_number"].upper() == flight_number:
                return Flight(
                    flight_number=flight_data["flight_number"],
                    origin=flight_data["origin"],
                    origin_city=flight_data["origin_city"],
                    destination=flight_data["destination"],
                    destination_city=flight_data["destination_city"],
                    departure_time=flight_data["departure_time"],
                    arrival_time=flight_data["arrival_time"],
                    duration=flight_data["duration"],
                    aircraft=flight_data["aircraft"],
                    price_economy=flight_data["price_economy"],
                    price_business=flight_data["price_business"],
                    available_seats=9,  # Default
                )

        return None

    def format_flight_for_display(self, flight: Flight) -> str:
        """Format a single flight for display"""
        return (
            f"✈️ **{flight.flight_number}** - {flight.origin_city} ({flight.origin}) "
            f"→ {flight.destination_city} ({flight.destination})\n"
            f"   ⏰ {flight.departure_time} - {flight.arrival_time} ({flight.duration})\n"
            f"   💺 {flight.aircraft}\n"
            f"   💰 Economy: ₹{flight.price_economy:,} | Business: ₹{flight.price_business:,}"
        )

    def format_flights_list(self, flights: list[Flight]) -> str:
        """Format a list of flights for display"""
        if not flights:
            return "No flights found for this route."

        output = f"Found {len(flights)} flight(s):\n\n"
        for flight in flights:
            output += self.format_flight_for_display(flight) + "\n\n"

        return output.strip()


# Singleton instance
_flight_service: FlightService | None = None


def get_flight_service() -> FlightService:
    """Get the global FlightService instance"""
    global _flight_service
    if _flight_service is None:
        _flight_service = FlightService()
    return _flight_service
