from __future__ import annotations

"""Conversation metadata management for tracking chat sessions."""

import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

# In-memory store for conversation metadata
_conversations: dict[str, dict] = {}


def create_conversation(user_id: int) -> str:
    """Create a new conversation and return its thread_id."""
    thread_id = str(uuid.uuid4())
    _conversations[thread_id] = {
        "thread_id": thread_id,
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat(),
        "message_count": 0,
        "preview": "",
        "last_agent": None,
    }
    logger.info(f"Created conversation {thread_id} for user {user_id}")
    return thread_id


def update_conversation(thread_id: str, preview: str = "", agent: str = "") -> None:
    """Update conversation metadata after a message exchange."""
    if thread_id in _conversations:
        _conversations[thread_id]["message_count"] += 1
        if preview:
            _conversations[thread_id]["preview"] = preview[:100]
        if agent:
            _conversations[thread_id]["last_agent"] = agent


def get_conversation(thread_id: str) -> dict | None:
    """Get metadata for a specific conversation."""
    return _conversations.get(thread_id)


def list_conversations(user_id: int) -> list[dict]:
    """List all conversations for a user, sorted by creation time (newest first)."""
    user_convos = [
        conv for conv in _conversations.values() if conv["user_id"] == user_id
    ]
    return sorted(user_convos, key=lambda c: c["created_at"], reverse=True)


def delete_conversation(thread_id: str) -> bool:
    """Delete a conversation by thread_id."""
    if thread_id in _conversations:
        del _conversations[thread_id]
        logger.info(f"Deleted conversation {thread_id}")
        return True
    return False
