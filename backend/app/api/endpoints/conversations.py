from __future__ import annotations

"""Conversation management endpoints — list, retrieve, and delete conversations."""

import logging

from fastapi import APIRouter, HTTPException

from app.memory.conversation_store import (
    delete_conversation,
    get_conversation,
    list_conversations,
)
from app.memory.checkpointer import get_checkpointer
from app.schemas.chat import ConversationListItem, ConversationMessage

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{user_id}", response_model=list[ConversationListItem])
async def get_user_conversations(user_id: int):
    """List all conversations for a user."""
    conversations = list_conversations(user_id)
    return [ConversationListItem(**conv) for conv in conversations]


@router.get("/{thread_id}/messages", response_model=list[ConversationMessage])
async def get_conversation_messages(thread_id: str):
    """Get all messages in a conversation."""
    conv = get_conversation(thread_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Retrieve messages from checkpointer
    checkpointer = get_checkpointer()
    config = {"configurable": {"thread_id": thread_id}}

    try:
        checkpoint = checkpointer.get(config)
        if not checkpoint:
            return []

        messages = []
        channel_values = checkpoint.get("channel_values", {})
        raw_messages = channel_values.get("messages", [])

        for msg in raw_messages:
            role = "user" if msg.type == "human" else "assistant"
            # Skip tool messages and system messages
            if msg.type in ("tool", "system"):
                continue
            if not msg.content:
                continue

            messages.append(ConversationMessage(
                role=role,
                content=msg.content,
                agent=None,  # Could be enriched from metadata
            ))

        return messages

    except Exception as e:
        logger.error(f"Failed to retrieve messages for {thread_id}: {e}")
        return []


@router.delete("/{thread_id}")
async def delete_conversation_endpoint(thread_id: str):
    """Delete a conversation."""
    success = delete_conversation(thread_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "deleted", "thread_id": thread_id}
