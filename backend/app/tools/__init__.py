"""
LangChain Tools for Air India Assistant

This module exports all available tools for the chat agent.
"""

from app.tools.flight_tools import FLIGHT_TOOLS, get_flight_details, search_flights

# All tools available for the agent
ALL_TOOLS = FLIGHT_TOOLS

__all__ = ["ALL_TOOLS", "search_flights", "get_flight_details"]
