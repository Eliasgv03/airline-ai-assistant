"""
Chat API Endpoint

This module exposes the chat functionality via a REST API.
It uses the ChatService to process messages and return responses.
"""

import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

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


@router.post("/stream")
async def chat_stream(request: ChatRequest, chat_service: ChatService = Depends(get_chat_service)):
    """
    Process a chat message and stream the assistant's response in real-time.

    This endpoint:
    1. Accepts a user message and session ID
    2. Streams response chunks as they are generated
    3. Uses Server-Sent Events (SSE) format

    Returns:
        StreamingResponse with text/event-stream content type
    """
    logger.info(f"Received streaming chat request for session: {request.session_id}")

    async def generate():
        """Generate SSE-formatted response chunks"""
        try:
            async for chunk in chat_service.process_message_stream(
                session_id=request.session_id, user_message=request.message
            ):
                # Format as SSE (Server-Sent Events)
                # Each chunk is sent as: data: {json}\n\n
                data = json.dumps({"chunk": chunk, "session_id": request.session_id})
                yield f"data: {data}\n\n"

            # Send completion signal
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            error_data = json.dumps({"error": str(e), "session_id": request.session_id})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
