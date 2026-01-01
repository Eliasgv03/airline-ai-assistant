"""
Chat Models

Pydantic schemas for chat API request/response validation.
"""

from typing import Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    """A single message in a conversation."""

    role: Literal["user", "assistant", "system"] = Field(
        ..., description="The role of the message sender"
    )
    content: str = Field(..., min_length=1, description="The message content")


class ChatRequest(BaseModel):
    """Request body for chat endpoints."""

    session_id: str = Field(
        ...,
        min_length=1,
        description="Unique conversation session identifier",
        examples=["session_abc123"],
    )
    message: str = Field(
        ...,
        min_length=1,
        description="User's message to the Maharaja assistant",
        examples=["What's the baggage allowance?", "Find flights from Delhi to Mumbai"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "user_12345",
                    "message": "What's the baggage allowance for international flights?",
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    """Response body from chat endpoints."""

    session_id: str = Field(..., description="The session ID from the request")
    message: str = Field(..., description="The Maharaja assistant's response")
    metadata: dict | None = Field(
        default=None, description="Additional metadata (role, provider, etc.)"
    )
