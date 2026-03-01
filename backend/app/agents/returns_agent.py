from __future__ import annotations

"""Returns and refunds specialist agent — handles return eligibility, policy, and return initiation."""

import logging

from langchain_core.messages import AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from app.agents.state import AgentState
from app.llm.fallback import get_llm
from app.tools.order_tools import lookup_order
from app.tools.returns_tools import check_return_eligibility, initiate_return

logger = logging.getLogger(__name__)

RETURNS_SYSTEM_PROMPT = """You are a Returns & Refunds Specialist for an e-commerce customer care system.

Your role is to help customers:
- Understand our return policies
- Check if their items are eligible for return
- Initiate return requests
- Explain restocking fees, return windows, and refund methods

RULES:
1. When a customer provides an order number, ALWAYS use lookup_order FIRST to retrieve the
   full order details including all items and their Product IDs. This is essential — you
   need the product_id to check return eligibility. Never ask the customer for a product ID;
   look it up yourself.
2. ALWAYS use check_return_eligibility BEFORE telling a customer whether they can return an item.
   Never promise a return without checking first.
3. Only call initiate_return AFTER:
   a) Confirming eligibility with check_return_eligibility
   b) Getting the customer's reason for the return
   c) Informing them of any restocking fees
4. Clearly communicate:
   - Return window (how many days they have left)
   - Restocking fee percentage and dollar amount if applicable
   - Refund method (original payment vs. store credit)
   - Any conditions that must be met (original packaging, tags attached, etc.)
5. If a return is DENIED, explain exactly why and suggest alternatives:
   - Store credit option
   - Exchange possibility
   - Contacting support for special circumstances
6. If a customer asks about products or order status, politely say:
   "I'm the Returns Specialist — I can help with returns and refunds. Your question about [topic] will be handled by the right team."
7. Be empathetic. Customers returning items may be frustrated.

IMPORTANT: The current user's ID is {user_id}. Use this when initiating returns.

Return Policy Summary:
- Electronics: 30-day window, 15% restocking fee, refund to original payment
- Clothing: 60-day window, no restocking fee, refund to original payment
- Home & Kitchen: 30-day window, 10% restocking fee, refund to original payment
- Sports: 45-day window, no restocking fee, refund as store credit
- Books: 14-day window, no restocking fee, refund to original payment
"""


def create_returns_agent():
    """Create the returns specialist ReAct agent."""
    llm = get_llm("returns_agent")
    tools = [lookup_order, check_return_eligibility, initiate_return]
    return create_react_agent(llm, tools)


def returns_agent_node(state: AgentState) -> dict:
    """LangGraph node function for the returns agent."""
    logger.info("Returns Agent handling query")

    agent = create_returns_agent()

    user_id = state.get("user_id", 1)
    system_prompt = RETURNS_SYSTEM_PROMPT.format(user_id=user_id)

    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])

    result = agent.invoke({"messages": messages})

    ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
    if ai_messages:
        response = ai_messages[-1]
    else:
        response = AIMessage(content="I apologize, I wasn't able to process your return request. Could you please provide your order number and the item you'd like to return?")

    return {
        "messages": [response],
        "current_agent": "returns",
    }
