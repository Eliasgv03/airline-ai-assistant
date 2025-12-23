from fastapi import APIRouter

from app.api import chat, flights

api_router = APIRouter()
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(flights.router, prefix="/flights", tags=["flights"])
