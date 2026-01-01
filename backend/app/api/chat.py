"""
Chat API Endpoints

Provides conversational AI capabilities for the Air India Maharaja assistant.
Supports both synchronous and streaming (SSE) response modes.
"""

import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService, get_chat_service
from app.utils.logger import get_logger

router = APIRouter(tags=["chat"])
logger = get_logger(__name__)


@router.post(
    "/",
    response_model=ChatResponse,
    summary="Send a message to the Maharaja assistant",
    description="""
Send a message and receive a complete response from the AI assistant.

**Features:**
- Automatic language detection (English, Hindi, Spanish, Portuguese, French)
- RAG-powered responses using Air India policy documents
- Flight search via natural language ("Find flights from Delhi to Mumbai")
- Maintains conversation context within session

**Example queries:**
- "What's the baggage allowance for international flights?"
- "Find flights from Delhi to Mumbai tomorrow"
- "¿Cuál es la política de cancelación?"
- "दिल्ली से मुंबई की फ्लाइट दिखाओ"
    """,
)
async def chat(
    request: ChatRequest, chat_service: ChatService = Depends(get_chat_service)
) -> ChatResponse:
    """Process a chat message and return the assistant's response."""
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


@router.post(
    "/stream",
    summary="Stream a response from the Maharaja assistant",
    description="""
Send a message and receive a streaming response via Server-Sent Events (SSE).

**Response format:**
```
data: {"chunk": "Hello", "session_id": "abc123"}
data: {"chunk": " there!", "session_id": "abc123"}
data: {"done": true}
```

**Use cases:**
- Real-time typing effect in chat UI
- Long responses (flight search results)
- Better user experience with immediate feedback
    """,
)
async def chat_stream(request: ChatRequest, chat_service: ChatService = Depends(get_chat_service)):
    """Process a chat message and stream the assistant's response in real-time."""
    logger.info(f"Received streaming chat request for session: {request.session_id}")

    async def generate():
        """Generate SSE-formatted response chunks."""
        try:
            async for chunk in chat_service.process_message_stream(
                session_id=request.session_id, user_message=request.message
            ):
                data = json.dumps({"chunk": chunk, "session_id": request.session_id})
                yield f"data: {data}\n\n"

            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            error_data = json.dumps({"error": str(e), "session_id": request.session_id})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get(
    "/sessions",
    summary="List active chat sessions",
    description="Returns a list of all active session IDs. Useful for debugging and monitoring.",
)
async def get_sessions(chat_service: ChatService = Depends(get_chat_service)) -> list[str]:
    """Get list of active session IDs."""
    from app.services.memory_service import get_memory_service

    memory_service = get_memory_service()
    session_ids = memory_service.get_all_session_ids()
    logger.info(f"Retrieved {len(session_ids)} active sessions")
    return session_ids
