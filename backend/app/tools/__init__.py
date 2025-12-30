"""
LangChain Tools for Air India Assistant

This module exports all available tools for the chat agent.
"""

from app.tools.flight_tools import FLIGHT_TOOLS, get_flight_details, search_flights
from app.tools.iata_tools import IATA_TOOLS, lookup_iata_code

# All tools available for the agent
ALL_TOOLS = FLIGHT_TOOLS + IATA_TOOLS

__all__ = ["ALL_TOOLS", "search_flights", "get_flight_details", "lookup_iata_code"]
