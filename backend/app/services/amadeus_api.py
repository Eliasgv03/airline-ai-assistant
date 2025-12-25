"""
Real Flight API Integration using Amadeus

This service integrates with Amadeus Flight Offers Search API to provide
real-time flight data with automatic fallback to mock data.
"""

import os
from datetime import datetime, timedelta

from amadeus import Client, ResponseError

from app.models.flight import Flight
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AmadeusFlightAPI:
    """Amadeus Flight API client with authentication and search capabilities"""

    def __init__(self):
        self.api_key = os.getenv("AMADEUS_API_KEY")
        self.api_secret = os.getenv("AMADEUS_API_SECRET")
        self.use_test_env = os.getenv("AMADEUS_USE_TEST", "true").lower() == "true"
        self.timeout = int(os.getenv("FLIGHT_API_TIMEOUT", "5"))

        self.client: Client | None = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Amadeus client with credentials"""
        if not self.api_key or not self.api_secret:
            logger.warning(
                "⚠️ Amadeus API credentials not configured. "
                "Set AMADEUS_API_KEY and AMADEUS_API_SECRET in .env"
            )
            return

        try:
            self.client = Client(
                client_id=self.api_key,
                client_secret=self.api_secret,
                hostname="test" if self.use_test_env else "production",
            )
            logger.info(
                f"✅ Amadeus API client initialized "
                f"({'TEST' if self.use_test_env else 'PRODUCTION'} environment)"
            )
        except Exception as e:
            logger.error(f"❌ Failed to initialize Amadeus client: {e}")
            self.client = None

    def is_configured(self) -> bool:
        """Check if API is properly configured"""
        return self.client is not None

    async def search_flights(
        self,
        origin: str,
        destination: str,
        date: str | None = None,
        adults: int = 1,
        max_results: int = 10,
    ) -> list[Flight]:
        """
        Search for flights using Amadeus API

        Args:
            origin: Origin airport code (e.g., "DEL", "BOM")
            destination: Destination airport code
            date: Departure date in YYYY-MM-DD format (defaults to tomorrow)
            adults: Number of adult passengers
            max_results: Maximum number of results to return

        Returns:
            List of Flight objects

        Raises:
            Exception: If API call fails
        """
        if not self.is_configured():
            raise Exception("Amadeus API not configured")

        # Type guard: at this point, client is guaranteed to be not None
        assert self.client is not None

        # Default to tomorrow if no date provided
        if not date or date == "any":
            departure_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            # Parse date (handle "today", "tomorrow", or specific date)
            if date.lower() == "today":
                departure_date = datetime.now().strftime("%Y-%m-%d")
            elif date.lower() == "tomorrow":
                departure_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            else:
                departure_date = date

        logger.info(f"🌐 Searching Amadeus API: {origin} → {destination} on {departure_date}")

        try:
            # Call Amadeus Flight Offers Search API
            response = self.client.shopping.flight_offers_search.get(
                originLocationCode=origin.upper(),
                destinationLocationCode=destination.upper(),
                departureDate=departure_date,
                adults=adults,
                max=max_results,
            )

            # Parse response
            flights = self._parse_amadeus_response(response.data)
            logger.info(f"✅ Found {len(flights)} flights from Amadeus API")
            return flights

        except ResponseError as error:
            logger.error(f"❌ Amadeus API error: {error}")
            raise Exception(f"Amadeus API error: {error.description}") from error
        except Exception as e:
            logger.error(f"❌ Unexpected error calling Amadeus API: {e}")
            raise

    def _parse_amadeus_response(self, data: list) -> list[Flight]:
        """
        Parse Amadeus API response into Flight objects

        Args:
            data: Raw Amadeus API response data

        Returns:
            List of Flight objects
        """
        flights = []

        for offer in data:
            try:
                # Extract itinerary (first segment for simplicity)
                itinerary = offer["itineraries"][0]
                segments = itinerary["segments"]
                first_segment = segments[0]
                last_segment = segments[-1]

                # Extract pricing
                price_info = offer["price"]
                total_price = float(price_info["total"])

                # Extract carrier info
                carrier_code = first_segment["carrierCode"]
                flight_number = f"{carrier_code} {first_segment['number']}"

                # Extract times
                departure_time = first_segment["departure"]["at"]
                arrival_time = last_segment["arrival"]["at"]

                # Calculate duration
                duration = itinerary["duration"]  # ISO 8601 format (e.g., "PT2H15M")
                duration_formatted = self._format_duration(duration)

                # Create Flight object
                flight = Flight(
                    flight_number=flight_number,
                    origin=first_segment["departure"]["iataCode"],
                    origin_city=first_segment["departure"].get("cityName", ""),
                    destination=last_segment["arrival"]["iataCode"],
                    destination_city=last_segment["arrival"].get("cityName", ""),
                    departure_time=self._format_time(departure_time),
                    arrival_time=self._format_time(arrival_time),
                    duration=duration_formatted,
                    aircraft=first_segment.get("aircraft", {}).get("code", "Unknown"),
                    price_economy=int(total_price),  # Simplified pricing
                    price_business=int(total_price * 2.5),  # Estimate
                    available_seats=offer.get("numberOfBookableSeats", 9),
                )

                flights.append(flight)

            except Exception as e:
                logger.warning(f"⚠️ Failed to parse flight offer: {e}")
                continue

        return flights

    def _format_duration(self, iso_duration: str) -> str:
        """
        Convert ISO 8601 duration to human-readable format

        Args:
            iso_duration: Duration in ISO 8601 format (e.g., "PT2H15M")

        Returns:
            Formatted duration (e.g., "2h 15m")
        """
        # Remove "PT" prefix
        duration = iso_duration.replace("PT", "")

        # Extract hours and minutes
        hours = 0
        minutes = 0

        if "H" in duration:
            hours_str, duration = duration.split("H")
            hours = int(hours_str)

        if "M" in duration:
            minutes = int(duration.replace("M", ""))

        return f"{hours}h {minutes}m"

    def _format_time(self, iso_time: str) -> str:
        """
        Convert ISO 8601 datetime to time string

        Args:
            iso_time: Time in ISO 8601 format (e.g., "2024-12-26T09:30:00")

        Returns:
            Formatted time (e.g., "09:30")
        """
        try:
            dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
            return dt.strftime("%H:%M")
        except Exception:
            return iso_time


# Singleton instance
_amadeus_api: AmadeusFlightAPI | None = None


def get_amadeus_api() -> AmadeusFlightAPI:
    """Get the global AmadeusFlightAPI instance"""
    global _amadeus_api
    if _amadeus_api is None:
        _amadeus_api = AmadeusFlightAPI()
    return _amadeus_api
