"""LangGraph checkpointer configuration for conversation persistence."""

import logging

from langgraph.checkpoint.memory import MemorySaver

from app.config import get_settings

logger = logging.getLogger(__name__)

# Singleton checkpointer instance
_checkpointer = None


def get_checkpointer() -> MemorySaver:
    """Get the LangGraph checkpointer instance.

    Uses InMemorySaver for development. In production, this could be
    swapped for a Redis-backed or database-backed checkpointer.
    """
    global _checkpointer

    if _checkpointer is None:
        settings = get_settings()
        logger.info(
            f"Initializing MemorySaver checkpointer (env: {settings.environment})"
        )
        _checkpointer = MemorySaver()

    return _checkpointer
