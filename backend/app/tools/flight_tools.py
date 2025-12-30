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
    """Input schema for flight search - MUST use IATA 3-letter airport codes"""

    origin: str = Field(
        description=(
            "Origin airport as a 3-letter IATA code (REQUIRED). "
            "You MUST convert city names to their IATA codes. "
            "Common mappings: Delhi=DEL, Mumbai=BOM, Bangalore=BLR, Chennai=MAA, "
            "Kolkata=CCU, Hyderabad=HYD, Goa=GOI, London=LHR, New York=JFK, "
            "Dubai=DXB, Singapore=SIN, Paris=CDG, Tokyo=NRT, Bangkok=BKK, "
            "Beijing=PEK, Shanghai=PVG, Hong Kong=HKG, Sydney=SYD, Los Angeles=LAX. "
            "ALWAYS use 3-letter uppercase codes like 'DEL', 'BOM', 'PEK'."
        )
    )
    destination: str = Field(
        description=(
            "Destination airport as a 3-letter IATA code (REQUIRED). "
            "You MUST convert city names to their IATA codes. "
            "Common mappings: Delhi=DEL, Mumbai=BOM, Bangalore=BLR, Chennai=MAA, "
            "Kolkata=CCU, Hyderabad=HYD, Goa=GOI, London=LHR, New York=JFK, "
            "Dubai=DXB, Singapore=SIN, Paris=CDG, Tokyo=NRT, Bangkok=BKK, "
            "Beijing=PEK, Shanghai=PVG, Hong Kong=HKG, Sydney=SYD, Los Angeles=LAX. "
            "ALWAYS use 3-letter uppercase codes like 'DEL', 'BOM', 'PEK'."
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


def _search_flights_sync(origin: str, destination: str, date: str = "tomorrow") -> str:
    """Sync wrapper for search_flights (for benchmark and non-async contexts)"""
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(_search_flights_impl(origin, destination, date))


search_flights = StructuredTool.from_function(
    func=_search_flights_sync,
    coroutine=_search_flights_impl,
    name="search_flights",
    description=(
        "Search for Air India flights between two airports. "
        "Use when users ask about flight schedules, times, availability, or prices. "
        "CRITICAL: You MUST convert city names to 3-letter IATA airport codes. "
        "Examples: 'Beijing' → 'PEK', 'Delhi' → 'DEL', 'Mumbai' → 'BOM', "
        "'London' → 'LHR', 'New York' → 'JFK', 'Tokyo' → 'NRT'. "
        "Also convert dates like 'tomorrow' or 'January 2nd' to YYYY-MM-DD format."
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
