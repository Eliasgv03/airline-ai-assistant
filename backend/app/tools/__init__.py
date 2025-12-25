"""
LangChain Tools for Air India Assistant

This module defines tools that the agent can use to perform specific tasks.
"""

from langchain.tools import tool

from app.services.flight_service import get_flight_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


@tool
async def search_flights(origin: str, destination: str, date: str = "any") -> str:
    """
    Search for Air India flights between two cities.

    Use this tool when users ask about:
    - Flight schedules or availability
    - Flight times or departure/arrival information
    - Flight prices or fares
    - Available flights on a route

    Args:
        origin: Origin city or airport code (e.g., "Delhi", "DEL", "Mumbai", "BOM")
        destination: Destination city or airport code (e.g., "Bangalore", "BLR", "London", "LHR")
        date: Travel date - can be "today", "tomorrow", "any", or a specific date

    Returns:
        Formatted flight information as a string with flight numbers, times, prices, and aircraft details
    """
    logger.info(f"🔧 Tool called: search_flights({origin}, {destination}, {date})")

    flight_service = get_flight_service()

    try:
        # Search for flights (async)
        flights = await flight_service.search_flights(
            origin=origin, destination=destination, date=date if date != "any" else None
        )

        if not flights:
            return (
                f"No Air India flights found from {origin} to {destination}. "
                f"Please check if the city names or airport codes are correct, "
                f"or try a different route."
            )

        # Format results
        result = flight_service.format_flights_list(flights)

        logger.info(f"✅ Returning {len(flights)} flights for {origin} → {destination}")
        return result

    except Exception as e:
        logger.error(f"❌ Error in search_flights tool: {str(e)}")
        return f"Sorry, I encountered an error while searching for flights: {str(e)}"


@tool
def get_flight_details(flight_number: str) -> str:
    """
    Get detailed information about a specific Air India flight by its flight number.

    Use this tool when users ask about a specific flight, such as:
    - "Tell me about flight AI 865"
    - "What time does AI 677 depart?"
    - "Details of the 9:30 flight" (if flight number was mentioned earlier in conversation)

    Args:
        flight_number: Air India flight number (e.g., "AI 865", "AI677", "865")

    Returns:
        Detailed flight information including route, times, aircraft, and prices
    """
    logger.info(f"🔧 Tool called: get_flight_details({flight_number})")

    flight_service = get_flight_service()

    try:
        # Normalize flight number (add "AI" prefix if missing)
        if not flight_number.upper().startswith("AI"):
            flight_number = f"AI {flight_number}"

        flight = flight_service.get_flight_by_number(flight_number)

        if not flight:
            return (
                f"Flight {flight_number} not found. "
                f"Please check the flight number and try again."
            )

        # Format single flight details
        result = flight_service.format_flight_for_display(flight)

        logger.info(f"✅ Returning details for flight {flight_number}")
        return result

    except Exception as e:
        logger.error(f"❌ Error in get_flight_details tool: {str(e)}")
        return f"Sorry, I encountered an error while getting flight details: {str(e)}"


# List of all available tools
ALL_TOOLS = [search_flights, get_flight_details]
