"""
Flight Search Service

Provides flight search functionality with flexible matching and filtering.
"""


from app.data.flight_data import FLIGHTS_DB, normalize_location
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FlightService:
    """Service for searching and filtering flights"""

    def __init__(self):
        self.flights_db = FLIGHTS_DB
        logger.info(f"FlightService initialized with {len(self.flights_db)} flights")

    def search_flights(
        self, origin: str, destination: str, date: str | None = None, max_results: int = 10
    ) -> list[dict]:
        """
        Search for flights between two locations.

        Args:
            origin: Origin city or airport code (e.g., "Delhi", "DEL")
            destination: Destination city or airport code (e.g., "Mumbai", "BOM")
            date: Optional date filter (e.g., "today", "tomorrow", "2024-12-25")
            max_results: Maximum number of results to return

        Returns:
            List of matching flights sorted by departure time
        """
        logger.info(f"Searching flights: {origin} -> {destination}, date={date}")

        # Normalize locations to airport codes
        origin_code = normalize_location(origin)
        dest_code = normalize_location(destination)

        logger.debug(f"Normalized: {origin_code} -> {dest_code}")

        # Filter flights by route
        matching_flights = [
            flight
            for flight in self.flights_db
            if flight["origin"] == origin_code and flight["destination"] == dest_code
        ]

        if not matching_flights:
            logger.info(f"No flights found for route {origin_code} -> {dest_code}")
            return []

        # TODO: Filter by date if provided (for now, return all)
        # In a real implementation, you would check flight availability for specific dates

        # Sort by departure time
        matching_flights.sort(key=lambda f: f["departure_time"])

        # Limit results
        results = matching_flights[:max_results]

        logger.info(f"Found {len(results)} flights for {origin_code} -> {dest_code}")
        return results

    def get_flight_by_number(self, flight_number: str) -> dict | None:
        """
        Get flight details by flight number.

        Args:
            flight_number: Flight number (e.g., "AI 865")

        Returns:
            Flight details or None if not found
        """
        flight_number = flight_number.upper().strip()

        for flight in self.flights_db:
            if flight["flight_number"].upper() == flight_number:
                return flight

        return None

    def format_flight_for_display(self, flight: dict) -> str:
        """
        Format a single flight for display.

        Args:
            flight: Flight dictionary

        Returns:
            Formatted string
        """
        return (
            f"✈️ **{flight['flight_number']}** - {flight['origin_city']} ({flight['origin']}) "
            f"→ {flight['destination_city']} ({flight['destination']})\n"
            f"   ⏰ {flight['departure_time']} - {flight['arrival_time']} ({flight['duration']})\n"
            f"   💺 {flight['aircraft']}\n"
            f"   💰 Economy: ₹{flight['price_economy']:,} | Business: ₹{flight['price_business']:,}"
        )

    def format_flights_list(self, flights: list[dict]) -> str:
        """
        Format a list of flights for display.

        Args:
            flights: List of flight dictionaries

        Returns:
            Formatted string with all flights
        """
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
