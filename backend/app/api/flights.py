"""
Flights API Endpoints

Provides REST API for flight search functionality using Amadeus API.
Supports both IATA codes and city names with automatic resolution.
"""

from datetime import date

from fastapi import APIRouter, Query

from app.services.flight_service import get_flight_service

router = APIRouter(prefix="/flights", tags=["flights"])


@router.get(
    "/search",
    summary="Search for available flights",
    description="""
Search for Air India flights between two cities or airports.

**Supported input formats:**
- City names: "Delhi", "Mumbai", "New York"
- IATA codes: "DEL", "BOM", "JFK"
- Mixed: "Delhi" → "BOM"

**Example requests:**
- `/flights/search?origin=Delhi&destination=Mumbai`
- `/flights/search?origin=DEL&destination=BOM&date=2024-12-31`

**Note:** Uses Amadeus API for real flight data with mock fallback.
    """,
)
async def search_flights(
    origin: str = Query(
        ...,
        min_length=2,
        max_length=50,
        description="Origin city name or IATA code (e.g., 'Delhi' or 'DEL')",
        examples=["Delhi", "DEL", "Mumbai"],
    ),
    destination: str = Query(
        ...,
        min_length=2,
        max_length=50,
        description="Destination city name or IATA code (e.g., 'Mumbai' or 'BOM')",
        examples=["Mumbai", "BOM", "Bangalore"],
    ),
    date_: date | None = Query(
        default=None,
        alias="date",
        description="Departure date in YYYY-MM-DD format (defaults to today)",
    ),
    max_results: int = Query(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of flights to return",
    ),
):
    """Search for available flights between origin and destination."""
    flight_service = get_flight_service()

    date_str = date_.isoformat() if date_ else None

    flights = await flight_service.search_flights(
        origin=origin,
        destination=destination,
        date=date_str,
        max_results=max_results,
    )

    return {
        "count": len(flights),
        "flights": [
            {
                "flight_number": f.flight_number,
                "origin": f.origin,
                "origin_city": f.origin_city,
                "destination": f.destination,
                "destination_city": f.destination_city,
                "departure_time": f.departure_time,
                "arrival_time": f.arrival_time,
                "duration": f.duration,
                "aircraft": f.aircraft,
                "price_economy": f.price_economy,
                "price_business": f.price_business,
                "available_seats": f.available_seats,
            }
            for f in flights
        ],
    }


@router.get("/{flight_number}")
async def get_flight_details(flight_number: str):
    """
    Get details for a specific flight by flight number.

    - **flight_number**: The flight number (e.g., "AI 865")

    Returns:
        Flight details or 404 if not found
    """
    flight_service = get_flight_service()
    flight = flight_service.get_flight_by_number(flight_number)

    if not flight:
        return {"error": f"Flight {flight_number} not found"}

    return {
        "flight_number": flight.flight_number,
        "origin": flight.origin,
        "origin_city": flight.origin_city,
        "destination": flight.destination,
        "destination_city": flight.destination_city,
        "departure_time": flight.departure_time,
        "arrival_time": flight.arrival_time,
        "duration": flight.duration,
        "aircraft": flight.aircraft,
        "price_economy": flight.price_economy,
        "price_business": flight.price_business,
        "available_seats": flight.available_seats,
    }
