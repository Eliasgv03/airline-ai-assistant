from datetime import date

from fastapi import APIRouter, Query

router = APIRouter(prefix="/flights", tags=["flights"])


@router.get("/search")
async def flights_search_stub(
    origin: str | None = Query(default=None, min_length=3, max_length=3),
    destination: str | None = Query(default=None, min_length=3, max_length=3),
    date_: date | None = Query(default=None, alias="date"),
):
    # TODO: Implement flight search functionality
    return {"results": [], "note": "Flight search not implemented yet"}
