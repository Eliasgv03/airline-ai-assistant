"""
Flights API endpoints

Provides REST API for flight search functionality.
Flight search is also available via the chatbot using natural language.
"""

from datetime import date

from fastapi import APIRouter, Query

from app.services.flight_service import get_flight_service

router = APIRouter(prefix="/flights", tags=["flights"])


@router.get("/search")
async def search_flights(
    origin: str = Query(
        ..., min_length=2, max_length=50, description="Origin city or airport code"
    ),
    destination: str = Query(
        ..., min_length=2, max_length=50, description="Destination city or airport code"
    ),
    date_: date | None = Query(default=None, alias="date", description="Optional departure date"),
    max_results: int = Query(default=5, ge=1, le=20, description="Maximum number of results"),
):
    """
    Search for available flights between origin and destination.

    - **origin**: City name (e.g., "Delhi") or airport code (e.g., "DEL")
    - **destination**: City name (e.g., "Mumbai") or airport code (e.g., "BOM")
    - **date**: Optional departure date (YYYY-MM-DD format)
    - **max_results**: Number of flights to return (1-20)

    Returns:
        List of available flights with prices and schedules
    """
    flight_service = get_flight_service()

    # Convert date to string if provided
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
