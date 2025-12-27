"""
Mock Flight Data for Air India

This module contains realistic Air India flight data for demonstration purposes.
Structure is designed to be easily replaceable with real API data.
"""

# Airport code mappings (includes common aliases and multilingual names)
AIRPORT_CODES = {
    # Indian cities - with aliases
    "delhi": "DEL",
    "new delhi": "DEL",
    "nueva delhi": "DEL",  # Spanish
    "neu-delhi": "DEL",  # German
    "mumbai": "BOM",
    "bombay": "BOM",  # Old name
    "bangalore": "BLR",
    "bengaluru": "BLR",
    "chennai": "MAA",
    "madras": "MAA",  # Old name
    "kolkata": "CCU",
    "calcutta": "CCU",  # Old name
    "hyderabad": "HYD",
    "goa": "GOI",
    "pune": "PNQ",
    "ahmedabad": "AMD",
    "jaipur": "JAI",
    "kochi": "COK",
    "cochin": "COK",
    # International cities - with aliases
    "london": "LHR",
    "londres": "LHR",  # Spanish
    "new york": "JFK",
    "nueva york": "JFK",  # Spanish
    "dubai": "DXB",
    "dubái": "DXB",  # Spanish
    "singapore": "SIN",
    "singapur": "SIN",  # Spanish
    "paris": "CDG",
    "parís": "CDG",  # Spanish
    "frankfurt": "FRA",
    "tokyo": "NRT",
    "tokio": "NRT",  # Spanish
    "bangkok": "BKK",
}

# Mock flight database
FLIGHTS_DB: list[dict] = [
    # Delhi - Mumbai route (high frequency)
    {
        "flight_number": "AI 865",
        "origin": "DEL",
        "origin_city": "Delhi",
        "destination": "BOM",
        "destination_city": "Mumbai",
        "departure_time": "06:00",
        "arrival_time": "08:10",
        "duration": "2h 10m",
        "aircraft": "Airbus A320",
        "price_economy": 4500,
        "price_business": 12000,
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "type": "domestic",
    },
    {
        "flight_number": "AI 677",
        "origin": "DEL",
        "origin_city": "Delhi",
        "destination": "BOM",
        "destination_city": "Mumbai",
        "departure_time": "09:30",
        "arrival_time": "11:45",
        "duration": "2h 15m",
        "aircraft": "Boeing 787",
        "price_economy": 5200,
        "price_business": 14000,
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "type": "domestic",
    },
    {
        "flight_number": "AI 863",
        "origin": "DEL",
        "origin_city": "Delhi",
        "destination": "BOM",
        "destination_city": "Mumbai",
        "departure_time": "14:15",
        "arrival_time": "16:30",
        "duration": "2h 15m",
        "aircraft": "Airbus A320",
        "price_economy": 4800,
        "price_business": 13000,
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "type": "domestic",
    },
    {
        "flight_number": "AI 805",
        "origin": "DEL",
        "origin_city": "Delhi",
        "destination": "BOM",
        "destination_city": "Mumbai",
        "departure_time": "18:00",
        "arrival_time": "20:15",
        "duration": "2h 15m",
        "aircraft": "Airbus A321",
        "price_economy": 5500,
        "price_business": 15000,
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "type": "domestic",
    },
    # Mumbai - Delhi route
    {
        "flight_number": "AI 866",
        "origin": "BOM",
        "origin_city": "Mumbai",
        "destination": "DEL",
        "destination_city": "Delhi",
        "departure_time": "07:00",
        "arrival_time": "09:15",
        "duration": "2h 15m",
        "aircraft": "Airbus A320",
        "price_economy": 4600,
        "price_business": 12500,
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "type": "domestic",
    },
    {
        "flight_number": "AI 678",
        "origin": "BOM",
        "origin_city": "Mumbai",
        "destination": "DEL",
        "destination_city": "Delhi",
        "departure_time": "12:00",
        "arrival_time": "14:20",
        "duration": "2h 20m",
        "aircraft": "Boeing 787",
        "price_economy": 5300,
        "price_business": 14500,
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "type": "domestic",
    },
    # Delhi - Bangalore route
    {
        "flight_number": "AI 503",
        "origin": "DEL",
        "origin_city": "Delhi",
        "destination": "BLR",
        "destination_city": "Bangalore",
        "departure_time": "08:00",
        "arrival_time": "10:45",
        "duration": "2h 45m",
        "aircraft": "Airbus A320",
        "price_economy": 5500,
        "price_business": 15000,
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "type": "domestic",
    },
    {
        "flight_number": "AI 807",
        "origin": "DEL",
        "origin_city": "Delhi",
        "destination": "BLR",
        "destination_city": "Bangalore",
        "departure_time": "15:30",
        "arrival_time": "18:15",
        "duration": "2h 45m",
        "aircraft": "Airbus A321",
        "price_economy": 6000,
        "price_business": 16000,
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "type": "domestic",
    },
    # Mumbai - Bangalore route
    {
        "flight_number": "AI 619",
        "origin": "BOM",
        "origin_city": "Mumbai",
        "destination": "BLR",
        "destination_city": "Bangalore",
        "departure_time": "10:00",
        "arrival_time": "11:30",
        "duration": "1h 30m",
        "aircraft": "Airbus A320",
        "price_economy": 4000,
        "price_business": 11000,
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "type": "domestic",
    },
    {
        "flight_number": "AI 623",
        "origin": "BOM",
        "origin_city": "Mumbai",
        "destination": "BLR",
        "destination_city": "Bangalore",
        "departure_time": "16:45",
        "arrival_time": "18:15",
        "duration": "1h 30m",
        "aircraft": "Airbus A320",
        "price_economy": 4200,
        "price_business": 11500,
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "type": "domestic",
    },
    # Mumbai - Goa route
    {
        "flight_number": "AI 631",
        "origin": "BOM",
        "origin_city": "Mumbai",
        "destination": "GOI",
        "destination_city": "Goa",
        "departure_time": "09:00",
        "arrival_time": "10:15",
        "duration": "1h 15m",
        "aircraft": "Airbus A319",
        "price_economy": 3500,
        "price_business": 9000,
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "type": "domestic",
    },
    {
        "flight_number": "AI 635",
        "origin": "BOM",
        "origin_city": "Mumbai",
        "destination": "GOI",
        "destination_city": "Goa",
        "departure_time": "14:30",
        "arrival_time": "15:45",
        "duration": "1h 15m",
        "aircraft": "Airbus A319",
        "price_economy": 3800,
        "price_business": 9500,
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "type": "domestic",
    },
    # International: Delhi - London
    {
        "flight_number": "AI 161",
        "origin": "DEL",
        "origin_city": "Delhi",
        "destination": "LHR",
        "destination_city": "London",
        "departure_time": "02:00",
        "arrival_time": "07:15",
        "duration": "9h 15m",
        "aircraft": "Boeing 787-8",
        "price_economy": 45000,
        "price_business": 180000,
        "days": ["Mon", "Wed", "Fri", "Sun"],
        "type": "international",
    },
    # International: Delhi - New York
    {
        "flight_number": "AI 101",
        "origin": "DEL",
        "origin_city": "Delhi",
        "destination": "JFK",
        "destination_city": "New York",
        "departure_time": "11:30",
        "arrival_time": "15:00",
        "duration": "15h 30m",
        "aircraft": "Boeing 777-300ER",
        "price_economy": 65000,
        "price_business": 250000,
        "days": ["Tue", "Thu", "Sat"],
        "type": "international",
    },
    # International: Mumbai - Dubai
    {
        "flight_number": "AI 971",
        "origin": "BOM",
        "origin_city": "Mumbai",
        "destination": "DXB",
        "destination_city": "Dubai",
        "departure_time": "04:00",
        "arrival_time": "06:15",
        "duration": "3h 15m",
        "aircraft": "Airbus A320",
        "price_economy": 18000,
        "price_business": 65000,
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "type": "international",
    },
    {
        "flight_number": "AI 975",
        "origin": "BOM",
        "origin_city": "Mumbai",
        "destination": "DXB",
        "destination_city": "Dubai",
        "departure_time": "21:00",
        "arrival_time": "23:15",
        "duration": "3h 15m",
        "aircraft": "Airbus A321",
        "price_economy": 19000,
        "price_business": 68000,
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "type": "international",
    },
    # International: Delhi - Singapore
    {
        "flight_number": "AI 381",
        "origin": "DEL",
        "origin_city": "Delhi",
        "destination": "SIN",
        "destination_city": "Singapore",
        "departure_time": "23:00",
        "arrival_time": "07:30",
        "duration": "6h 30m",
        "aircraft": "Boeing 787-8",
        "price_economy": 35000,
        "price_business": 140000,
        "days": ["Mon", "Wed", "Fri", "Sun"],
        "type": "international",
    },
]


def get_all_flights() -> list[dict]:
    """Return all flights in the database"""
    return FLIGHTS_DB


def get_airport_code(city_name: str) -> str | None:
    """
    Convert city name to airport code.

    Args:
        city_name: City name (e.g., "Delhi", "Mumbai")

    Returns:
        Airport code (e.g., "DEL", "BOM") or None if not found
    """
    normalized = city_name.lower().strip()
    return AIRPORT_CODES.get(normalized)


def normalize_location(location: str) -> str:
    """
    Normalize location to airport code.

    Args:
        location: City name or airport code

    Returns:
        Airport code (uppercase)
    """
    # If already an airport code (3 letters)
    if len(location) == 3 and location.isalpha():
        return location.upper()

    # Try to find city in mapping
    code = get_airport_code(location)
    if code:
        return code

    # Return as-is (uppercase)
    return location.upper()
