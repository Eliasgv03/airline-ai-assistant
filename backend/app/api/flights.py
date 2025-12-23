from datetime import date
from typing import Optional

from fastapi import APIRouter, Query

router = APIRouter(prefix="/flights", tags=["flights"])


@router.get("/search")
async def flights_search_stub(
    origin: Optional[str] = Query(default=None, min_length=3, max_length=3),
    destination: Optional[str] = Query(default=None, min_length=3, max_length=3),
    date_: Optional[date] = Query(default=None, alias="date"),
):
    # Stub temporal: no implementado aún
    return {"results": [], "note": "Flight search not implemented yet"}
