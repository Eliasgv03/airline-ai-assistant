from datetime import date, datetime

from pydantic import BaseModel, Field


class FlightSearchRequest(BaseModel):
    origin: str = Field(..., min_length=3, max_length=3, description="IATA origin code, e.g., DEL")
    destination: str = Field(
        ..., min_length=3, max_length=3, description="IATA destination code, e.g., BOM"
    )
    date: date = Field(..., description="Flight departure date (YYYY-MM-DD)")


class Flight(BaseModel):
    flightNo: str = Field(..., description="Airline + number, e.g., AI 677")
    origin: str = Field(..., min_length=3, max_length=3)
    destination: str = Field(..., min_length=3, max_length=3)
    departure: datetime
    arrival: datetime
    duration_minutes: int
    price: float
    currency: str = "INR"
    stops: int = 0
    aircraft: str | None = None


class FlightSearchResponse(BaseModel):
    results: list[Flight] = []
