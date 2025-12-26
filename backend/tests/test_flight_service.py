"""
Basic unit tests for flight service
"""

from app.services.flight_service import FlightService


class TestFlightService:
    """Test FlightService functionality"""

    def test_flight_service_initialization(self):
        """Test that FlightService initializes correctly"""
        service = FlightService()
        assert service is not None
        assert len(service.flights_db) > 0

    def test_normalize_location(self):
        """Test location normalization"""
        # Test using the imported normalize_location function
        from data.flight_data import normalize_location

        # Test airport codes
        assert normalize_location("DEL") == "DEL"
        assert normalize_location("del") == "DEL"

        # Test city names
        assert normalize_location("Delhi") == "DEL"
        assert normalize_location("Mumbai") == "BOM"

    def test_get_flight_by_number(self):
        """Test getting flight by number"""
        service = FlightService()

        # Test existing flight
        flight = service.get_flight_by_number("AI 865")
        assert flight is not None
        assert flight.flight_number == "AI 865"

        # Test non-existing flight
        flight = service.get_flight_by_number("XX 999")
        assert flight is None

    def test_format_flight_for_display(self):
        """Test flight formatting"""
        service = FlightService()
        flight = service.get_flight_by_number("AI 865")

        if flight:
            formatted = service.format_flight_for_display(flight)
            assert "AI 865" in formatted
            assert "✈️" in formatted
