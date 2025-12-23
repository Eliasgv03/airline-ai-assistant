from typing import Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, description="Conversation session identifier")
    message: str = Field(..., min_length=1, description="User message content")


class ChatResponse(BaseModel):
    session_id: str
    message: str
    metadata: dict | None = None
