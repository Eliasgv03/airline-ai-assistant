"""
Chat API Endpoint

This module exposes the chat functionality via a REST API.
It uses the ChatService to process messages and return responses.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService, get_chat_service
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest, chat_service: ChatService = Depends(get_chat_service)
) -> ChatResponse:
    """
    Process a chat message and return the assistant's response.

    This endpoint:
    1. Accepts a user message and session ID
    2. Routes it to the ChatService
    3. Returns the assistant's response with metadata
    """
    logger.info(f"Received chat request for session: {request.session_id}")

    try:
        response_text = chat_service.process_message(
            session_id=request.session_id, user_message=request.message
        )

        return ChatResponse(
            session_id=request.session_id, message=response_text, metadata={"role": "assistant"}
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e
