from __future__ import annotations

"""Router/Orchestrator agent — classifies customer intent and dispatches to specialists."""

import json
import logging

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agents.state import AgentState
from app.llm.fallback import get_llm

logger = logging.getLogger(__name__)

ROUTER_SYSTEM_PROMPT = """You are a Customer Service Router. Your ONLY job is to classify the customer's intent and decide which specialist agent should handle it.

Classify the customer's message into EXACTLY ONE of these categories:

- "product": Questions about products, searching for items, product features, comparisons, availability, recommendations, pricing
- "order": Questions about order status, shipping, tracking, delivery, order history, "where is my order"
- "returns": Questions about returns, refunds, exchanges, return policies, "I want to return"
- "escalation": Customer explicitly asks for a human/manager, expresses strong frustration, complaints, threats, or the issue spans multiple domains and is complex
- "general": Greetings (hello, hi), thank you messages, goodbyes, general store questions not specific to products/orders/returns

Respond with ONLY a JSON object, nothing else:
{
    "intent": "product|order|returns|escalation|general",
    "confidence": 0.0 to 1.0,
    "reasoning": "brief explanation"
}

Examples:
- "What laptops do you sell?" -> {"intent": "product", "confidence": 0.95, "reasoning": "Customer asking about product catalog"}
- "Where is my order ORD-2025-00123?" -> {"intent": "order", "confidence": 0.98, "reasoning": "Customer asking about order tracking"}
- "I want to return my headphones" -> {"intent": "returns", "confidence": 0.95, "reasoning": "Customer wants to initiate a return"}
- "Let me speak to a manager NOW" -> {"intent": "escalation", "confidence": 0.99, "reasoning": "Customer explicitly requesting human agent"}
- "Hello!" -> {"intent": "general", "confidence": 0.99, "reasoning": "Customer greeting"}
- "Thanks for your help!" -> {"intent": "general", "confidence": 0.95, "reasoning": "Customer expressing gratitude"}
"""

GENERAL_RESPONSE_PROMPT = """You are a friendly customer care assistant for an e-commerce store.
Respond to the customer's general message (greeting, thanks, goodbye, etc.) briefly and warmly.
Let them know you can help with:
- Product search and information
- Order tracking and status
- Returns and refunds

Keep it to 2-3 sentences max."""

CLARIFICATION_RESPONSE = (
    "I'd be happy to help! Could you provide a bit more detail about what you need? "
    "I can assist with:\n"
    "- **Product search** — finding products, comparing items, checking availability\n"
    "- **Order tracking** — checking order status, shipping updates, delivery info\n"
    "- **Returns & refunds** — return eligibility, initiating returns, refund status\n\n"
    "What would you like help with?"
)


def parse_router_response(content: str) -> dict:
    """Parse the router's JSON response, handling edge cases."""
    try:
        # Try to extract JSON from the response
        content = content.strip()

        # Handle markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        # Find JSON object in the string
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            json_str = content[start:end]
            return json.loads(json_str)
    except (json.JSONDecodeError, IndexError, ValueError) as e:
        logger.warning(f"Failed to parse router response: {e}")

    # Default fallback
    return {"intent": "general", "confidence": 0.3, "reasoning": "Failed to parse classification"}


def router_agent_node(state: AgentState) -> dict:
    """LangGraph node function for the router agent.

    Classifies intent and returns routing metadata. Does NOT generate
    the customer-facing response — that's the specialist's job.
    """
    logger.info("Router Agent classifying intent")

    llm = get_llm("router_agent")

    messages = [SystemMessage(content=ROUTER_SYSTEM_PROMPT)] + list(state["messages"])

    response = llm.invoke(messages)
    content = response.content if isinstance(response, AIMessage) else str(response)

    classification = parse_router_response(content)
    intent = classification.get("intent", "general")
    confidence = classification.get("confidence", 0.5)

    logger.info(f"Router classified: intent={intent}, confidence={confidence}, reasoning={classification.get('reasoning', '')}")

    # Handle low confidence
    if confidence < 0.6:
        intent = "clarify"

    # Handle general queries inline (router responds directly)
    if intent == "general":
        general_llm = get_llm("router_general")
        general_messages = [SystemMessage(content=GENERAL_RESPONSE_PROMPT)] + list(state["messages"])
        general_response = general_llm.invoke(general_messages)
        general_content = general_response.content if isinstance(general_response, AIMessage) else str(general_response)

        return {
            "messages": [AIMessage(content=general_content)],
            "current_agent": "router",
            "intent": "general",
            "confidence": confidence,
        }

    # Handle clarification needed
    if intent == "clarify":
        return {
            "messages": [AIMessage(content=CLARIFICATION_RESPONSE)],
            "current_agent": "router",
            "intent": "clarify",
            "confidence": confidence,
        }

    # For specialist intents, just update routing metadata (no message added)
    return {
        "intent": intent,
        "confidence": confidence,
        "current_agent": "router",
    }


def route_to_agent(state: AgentState) -> str:
    """Conditional edge function — determines which agent node to route to.

    Returns the node name as a string. LangGraph uses this to select
    the next node in the graph.
    """
    # Check escalation flag first (overrides intent)
    if state.get("escalation_needed"):
        return "escalation"

    intent = state.get("intent", "general")

    route_map = {
        "product": "product",
        "order": "order",
        "returns": "returns",
        "escalation": "escalation",
    }

    return route_map.get(intent, "__end__")
