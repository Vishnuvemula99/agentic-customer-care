from __future__ import annotations

"""Order tracking specialist agent — handles order status, shipping, and tracking."""

import logging

from langchain_core.messages import AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from app.agents.state import AgentState
from app.llm.fallback import get_llm
from app.tools.order_tools import get_order_status, get_user_orders, lookup_order

logger = logging.getLogger(__name__)

ORDER_SYSTEM_PROMPT = """You are an Order Tracking Specialist for an e-commerce customer care system.

Your role is to help customers:
- Check the status of their orders
- Provide shipping and tracking information
- Look up order details and items
- Provide estimated delivery dates

RULES:
1. If the customer provides an order number (like ORD-2025-XXXXX), use lookup_order or get_order_status directly.
2. If the customer doesn't provide an order number, use get_user_orders with their user_id to list all their orders.
   The user_id is provided in the conversation context.
3. NEVER fabricate tracking numbers, delivery dates, or order statuses. Only share data from tool results.
4. For "in_transit" orders, share the tracking number and carrier so the customer can track online.
5. For "pending" or "confirmed" orders, let the customer know the order is being processed.
6. For "cancelled" orders, inform the customer and suggest they place a new order if needed.
7. If a customer asks about products, returns, or anything outside order tracking, politely say:
   "I'm the Order Tracking Specialist — I can help with order status and shipping. Your question about [topic] will be handled by the right team."
8. Be empathetic if delivery is delayed. Provide clear, factual information.

IMPORTANT: The current user's ID is {user_id}. Use this when looking up orders without a specific order number.
"""


def create_order_agent():
    """Create the order tracking ReAct agent."""
    llm = get_llm("order_agent")
    tools = [lookup_order, get_order_status, get_user_orders]
    return create_react_agent(llm, tools)


def order_agent_node(state: AgentState) -> dict:
    """LangGraph node function for the order agent."""
    logger.info("Order Agent handling query")

    agent = create_order_agent()

    # Inject user_id into system prompt
    user_id = state.get("user_id", 1)
    system_prompt = ORDER_SYSTEM_PROMPT.format(user_id=user_id)

    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])

    result = agent.invoke({"messages": messages})

    ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
    if ai_messages:
        response = ai_messages[-1]
    else:
        response = AIMessage(content="I apologize, I wasn't able to look up your order information. Could you please provide your order number?")

    return {
        "messages": [response],
        "current_agent": "order",
    }
