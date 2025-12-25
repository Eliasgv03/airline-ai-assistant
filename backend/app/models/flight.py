from datetime import date as DateType

from pydantic import BaseModel, Field


class FlightSearchRequest(BaseModel):
    origin: str = Field(..., min_length=3, max_length=3, description="IATA origin code, e.g., DEL")
    destination: str = Field(
        ..., min_length=3, max_length=3, description="IATA destination code, e.g., BOM"
    )
    departure_date: DateType = Field(..., description="Flight departure date (YYYY-MM-DD)")


class Flight(BaseModel):
    """Flight model with all details"""

    flight_number: str = Field(..., description="Flight number, e.g., AI 865")
    origin: str = Field(..., min_length=3, max_length=3, description="Origin airport code")
    origin_city: str = Field(..., description="Origin city name")
    destination: str = Field(
        ..., min_length=3, max_length=3, description="Destination airport code"
    )
    destination_city: str = Field(..., description="Destination city name")
    departure_time: str = Field(..., description="Departure time (HH:MM)")
    arrival_time: str = Field(..., description="Arrival time (HH:MM)")
    duration: str = Field(..., description="Flight duration (e.g., '2h 15m')")
    aircraft: str = Field(..., description="Aircraft type")
    price_economy: int = Field(..., description="Economy class price in INR")
    price_business: int = Field(..., description="Business class price in INR")
    available_seats: int = Field(default=9, description="Available seats")


class FlightSearchResponse(BaseModel):
    results: list[Flight] = Field(default_factory=list)
