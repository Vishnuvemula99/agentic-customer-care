from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    """Request body for sending a chat message."""

    message: str = Field(..., min_length=1, max_length=2000, description="The user's message")
    thread_id: Optional[str] = Field(None, description="Conversation thread ID. None for new conversation.")
    user_id: int = Field(default=1, description="Mock user ID for demo")


class ChatMessageResponse(BaseModel):
    """Response body for a chat message."""

    response: str
    thread_id: str
    agent: str
    escalated: bool = False
    intent: str = ""


class StreamTokenEvent(BaseModel):
    """SSE event for a streamed token."""

    token: str


class StreamMetadataEvent(BaseModel):
    """SSE event for agent metadata."""

    agent: str


class ConversationListItem(BaseModel):
    """Summary of a conversation for the sidebar."""

    thread_id: str
    user_id: int
    created_at: str
    preview: str
    message_count: int
    last_agent: Optional[str] = None


class ConversationMessage(BaseModel):
    """A single message in a conversation."""

    role: str  # "user" or "assistant"
    content: str
    agent: Optional[str] = None
    timestamp: Optional[str] = None
