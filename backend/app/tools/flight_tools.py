"""
Flight Search Tools for Air India Assistant

This module defines LangChain tools for flight search and details.
Uses Pydantic schemas to guide LLM on expected input formats.
"""

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from app.services.flight_service import get_flight_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


# ============================================
# Pydantic Schemas for Tool Inputs
# ============================================


class FlightSearchInput(BaseModel):
    """Input schema for flight search with explicit format instructions"""

    origin: str = Field(
        description=(
            "Origin city name or IATA airport code. "
            "Examples: 'Delhi', 'DEL', 'Mumbai', 'BOM', 'New Delhi', 'Bangalore'. "
            "Prefer using the city name as spoken by the user."
        )
    )
    destination: str = Field(
        description=(
            "Destination city name or IATA airport code. "
            "Examples: 'Mumbai', 'BOM', 'London', 'LHR', 'New York', 'JFK'. "
            "Prefer using the city name as spoken by the user."
        )
    )
    date: str = Field(
        default="tomorrow",
        description=(
            "Travel date in one of these formats: "
            "'today', 'tomorrow', or YYYY-MM-DD format (e.g., '2025-01-02'). "
            "If user says a date like 'January 2nd' or '27 de diciembre', "
            "convert it to YYYY-MM-DD format. "
            "Default is 'tomorrow' if no date specified."
        ),
    )


class FlightDetailsInput(BaseModel):
    """Input schema for flight details lookup"""

    flight_number: str = Field(
        description=(
            "Air India flight number. "
            "Examples: 'AI 865', 'AI677', '865'. "
            "The 'AI' prefix is optional and will be added if missing."
        )
    )


# ============================================
# Tool Implementations
# ============================================


async def _search_flights_impl(origin: str, destination: str, date: str = "tomorrow") -> str:
    """Search for flights between two cities"""
    logger.info(f"🔧 Tool called: search_flights({origin}, {destination}, {date})")

    flight_service = get_flight_service()

    try:
        flights = await flight_service.search_flights(
            origin=origin,
            destination=destination,
            date=date if date not in ("any", "tomorrow") else None,
        )

        if not flights:
            return (
                f"No Air India flights found from {origin} to {destination}. "
                f"Please check if the city names or airport codes are correct, "
                f"or try a different route."
            )

        result = flight_service.format_flights_list(flights)
        logger.info(f"✅ Returning {len(flights)} flights for {origin} → {destination}")
        return result

    except Exception as e:
        logger.error(f"❌ Error in search_flights tool: {str(e)}")
        return f"Sorry, I encountered an error while searching for flights: {str(e)}"


def _get_flight_details_impl(flight_number: str) -> str:
    """Get details for a specific flight"""
    logger.info(f"🔧 Tool called: get_flight_details({flight_number})")

    flight_service = get_flight_service()

    try:
        # Normalize flight number (add "AI" prefix if missing)
        if not flight_number.upper().startswith("AI"):
            flight_number = f"AI {flight_number}"

        flight = flight_service.get_flight_by_number(flight_number)

        if not flight:
            return f"Flight {flight_number} not found. Please check the flight number."

        result = flight_service.format_flight_for_display(flight)
        logger.info(f"✅ Returning details for flight {flight_number}")
        return result

    except Exception as e:
        logger.error(f"❌ Error in get_flight_details tool: {str(e)}")
        return f"Sorry, I encountered an error: {str(e)}"


# ============================================
# Create Structured Tools with Schemas
# ============================================

search_flights = StructuredTool.from_function(
    coroutine=_search_flights_impl,
    name="search_flights",
    description=(
        "Search for Air India flights between two cities. "
        "Use when users ask about flight schedules, times, availability, or prices. "
        "IMPORTANT: Convert natural language dates to YYYY-MM-DD format."
    ),
    args_schema=FlightSearchInput,  # type: ignore[arg-type]
)

get_flight_details = StructuredTool.from_function(
    func=_get_flight_details_impl,
    name="get_flight_details",
    description=(
        "Get detailed information about a specific Air India flight by flight number. "
        "Use when users ask about a specific flight like 'AI 865'."
    ),
    args_schema=FlightDetailsInput,  # type: ignore[arg-type]
)


# List of all flight tools
FLIGHT_TOOLS = [search_flights, get_flight_details]
