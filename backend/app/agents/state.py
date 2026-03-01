from __future__ import annotations

"""Shared agent state definition for the LangGraph multi-agent system."""

from typing import Annotated, Any

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """State shared across all agents in the customer care graph.

    The `messages` field accumulates conversation history via the `add_messages`
    reducer. All other fields use last-writer-wins semantics.
    """

    # Conversation messages (accumulated via reducer)
    messages: Annotated[list[BaseMessage], add_messages]

    # Routing metadata
    current_agent: str          # Which specialist agent is active
    intent: str                 # Classified intent from router
    confidence: float           # Router's confidence in classification

    # User context
    user_id: int                # Authenticated user ID

    # Escalation
    escalation_needed: bool     # Flag for human escalation
    escalation_reason: str      # Why escalation was triggered

    # Shared context between agents
    context: dict[str, Any]     # Domain-specific data (order info, product info, etc.)

    # Conversation tracking
    turn_count: int             # Number of turns in current conversation
