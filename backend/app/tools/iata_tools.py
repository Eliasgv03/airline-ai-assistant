"""
IATA Code Lookup Tool for Air India Assistant

Provides LangChain tool for the agent to look up airport codes
when users mention cities that need to be converted to IATA codes.
"""

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from app.services.iata_service import get_iata_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


class IATALookupInput(BaseModel):
    """Input schema for IATA code lookup"""

    city_name: str = Field(
        description=(
            "Name of the city or airport to look up. "
            "Can be in any language. "
            "Examples: 'Delhi', 'New York', 'Londres', 'Tokyo', '東京'"
        )
    )


def _lookup_iata_code_impl(city_name: str) -> str:
    """
    Look up the IATA airport code for a city.

    Args:
        city_name: City name in any language

    Returns:
        IATA code information or error message
    """
    logger.info(f"🔧 Tool called: lookup_iata_code({city_name})")

    service = get_iata_service()
    code = service.lookup(city_name)

    if code:
        logger.info(f"✅ IATA code found: {city_name} → {code}")
        return f"The IATA airport code for {city_name} is: {code}"
    else:
        logger.warning(f"⚠️ IATA code not found: {city_name}")
        return (
            f"Could not find IATA code for '{city_name}'. "
            "Please verify the city name spelling or try the official airport name."
        )


lookup_iata_code = StructuredTool.from_function(
    func=_lookup_iata_code_impl,
    name="lookup_iata_code",
    description=(
        "Look up the 3-letter IATA airport code for a city or airport. "
        "Use this tool when a user mentions a city and you need to find "
        "its airport code before searching for flights. "
        "The tool supports city names in multiple languages. "
        "Examples: 'Cancún' → 'CUN', 'São Paulo' → 'GRU', '北京' → 'PEK'"
    ),
    args_schema=IATALookupInput,  # type: ignore[arg-type]
)


# List of IATA tools
IATA_TOOLS = [lookup_iata_code]
