from typing import Optional, Literal
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, description="Conversation session identifier")
    message: str = Field(..., min_length=1, description="User message content")
    system_prompt: Optional[str] = Field(default=None, description="Optional system prompt override")
    temperature: float = Field(default=0.3, ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    reply: str
    meta: Optional[dict] = None
