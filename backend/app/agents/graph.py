from __future__ import annotations

"""Main LangGraph StateGraph assembly — wires all agents into the conversation flow."""

import logging
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph

from app.agents.escalation_agent import escalation_agent_node
from app.agents.order_agent import order_agent_node
from app.agents.product_agent import product_agent_node
from app.agents.returns_agent import returns_agent_node
from app.agents.router_agent import route_to_agent, router_agent_node
from app.agents.state import AgentState
from app.memory.checkpointer import get_checkpointer

logger = logging.getLogger(__name__)

# Compiled graph singleton
_compiled_graph = None


def build_graph() -> StateGraph:
    """Build and compile the multi-agent customer care graph.

    Flow:
        User Message → Router → [Product | Order | Returns | Escalation] → END
                         ↓ (general/clarify)
                        END
    """
    graph = StateGraph(AgentState)

    # Add agent nodes
    graph.add_node("router", router_agent_node)
    graph.add_node("product", product_agent_node)
    graph.add_node("order", order_agent_node)
    graph.add_node("returns", returns_agent_node)
    graph.add_node("escalation", escalation_agent_node)

    # Entry point: every message starts at the router
    graph.set_entry_point("router")

    # Conditional routing from router to specialists
    graph.add_conditional_edges(
        "router",
        route_to_agent,
        {
            "product": "product",
            "order": "order",
            "returns": "returns",
            "escalation": "escalation",
            "__end__": END,  # general/clarify handled inline by router
        },
    )

    # All specialist agents route to END after responding
    graph.add_edge("product", END)
    graph.add_edge("order", END)
    graph.add_edge("returns", END)
    graph.add_edge("escalation", END)

    # Compile with checkpointer for multi-turn memory
    checkpointer = get_checkpointer()
    compiled = graph.compile(checkpointer=checkpointer)

    logger.info("Multi-agent customer care graph compiled successfully")
    return compiled


def get_graph():
    """Get or create the compiled graph singleton."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


def invoke_graph(
    message: str,
    thread_id: str,
    user_id: int = 1,
) -> dict[str, Any]:
    """Invoke the agent graph with a user message.

    Args:
        message: The user's message text.
        thread_id: Conversation thread ID for memory persistence.
        user_id: The authenticated user's ID.

    Returns:
        Dictionary with 'response' (str), 'agent' (str), and 'escalated' (bool).
    """
    graph = get_graph()

    # Build input state
    input_state = {
        "messages": [HumanMessage(content=message)],
        "user_id": user_id,
        "current_agent": "",
        "intent": "",
        "confidence": 0.0,
        "escalation_needed": False,
        "escalation_reason": "",
        "context": {},
        "turn_count": 0,
    }

    # Config with thread_id for checkpointer
    config = {"configurable": {"thread_id": thread_id}}

    try:
        result = graph.invoke(input_state, config=config)

        # Extract the last AI message
        messages = result.get("messages", [])
        response_text = ""
        for msg in reversed(messages):
            if hasattr(msg, "content") and msg.content and not isinstance(msg, HumanMessage):
                response_text = msg.content
                break

        return {
            "response": response_text or "I'm sorry, I couldn't process your request. Could you please try again?",
            "agent": result.get("current_agent", "router"),
            "escalated": result.get("escalation_needed", False),
            "intent": result.get("intent", ""),
        }

    except Exception as e:
        logger.error(f"Graph invocation failed: {e}", exc_info=True)
        return {
            "response": "I apologize, but I'm experiencing technical difficulties. Please try again in a moment.",
            "agent": "system",
            "escalated": False,
            "intent": "error",
        }


async def stream_graph(
    message: str,
    thread_id: str,
    user_id: int = 1,
):
    """Stream the agent graph response token by token.

    Yields dictionaries with event type and data for SSE streaming.
    """
    graph = get_graph()

    input_state = {
        "messages": [HumanMessage(content=message)],
        "user_id": user_id,
        "current_agent": "",
        "intent": "",
        "confidence": 0.0,
        "escalation_needed": False,
        "escalation_reason": "",
        "context": {},
        "turn_count": 0,
    }

    config = {"configurable": {"thread_id": thread_id}}

    try:
        # Use astream_events for token-level streaming
        current_agent = "router"

        async for event in graph.astream_events(input_state, config=config, version="v2"):
            event_type = event.get("event", "")

            # Track which agent is active
            if event_type == "on_chain_start" and event.get("name") in (
                "product", "order", "returns", "escalation", "router"
            ):
                current_agent = event["name"]
                yield {"event": "metadata", "data": {"agent": current_agent}}

            # Stream individual tokens
            elif event_type == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    yield {"event": "token", "data": {"token": chunk.content}}

        yield {"event": "done", "data": {"thread_id": thread_id, "agent": current_agent}}

    except Exception as e:
        logger.error(f"Stream graph failed: {e}", exc_info=True)
        yield {
            "event": "error",
            "data": {"message": "An error occurred while processing your request."},
        }
