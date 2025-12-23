from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])


class _StubChatRequest(BaseModel):
    session_id: str
    message: str


@router.post("")
async def chat_stub(_: _StubChatRequest):
    # Stub temporal: no implementado aún
    raise HTTPException(status_code=501, detail="Chat endpoint not implemented yet")
