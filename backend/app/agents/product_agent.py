from __future__ import annotations

"""Product specialist agent — handles product search, details, and comparisons."""

import logging

from langchain_core.messages import AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from app.agents.state import AgentState
from app.llm.fallback import get_llm
from app.tools.product_tools import compare_products, get_product_details, search_products

logger = logging.getLogger(__name__)

PRODUCT_SYSTEM_PROMPT = """You are a Product Specialist for an e-commerce customer care system.

Your role is to help customers:
- Find products in our catalog
- Answer questions about product features, specifications, and availability
- Compare products side by side
- Make product recommendations based on customer needs

RULES:
1. ALWAYS use the search_products tool before answering product questions. Never make up product information.
2. If a customer mentions a specific product, use get_product_details to get full information.
3. When comparing products, use the compare_products tool with the relevant product IDs.
4. If a customer asks about orders, returns, billing, or anything outside product queries, politely say:
   "I'm the Product Specialist — I can help with product questions. Your question about [topic] will be handled by the right team."
5. Be helpful, concise, and accurate. Only share information from tool results.
6. If a product is out of stock, let the customer know and suggest similar alternatives.
7. Format prices clearly with $ symbol.
"""


def create_product_agent():
    """Create the product specialist ReAct agent."""
    llm = get_llm("product_agent")
    tools = [search_products, get_product_details, compare_products]
    return create_react_agent(llm, tools)


def product_agent_node(state: AgentState) -> dict:
    """LangGraph node function for the product agent."""
    logger.info("Product Agent handling query")

    agent = create_product_agent()

    # Build messages with system prompt
    messages = [SystemMessage(content=PRODUCT_SYSTEM_PROMPT)] + list(state["messages"])

    result = agent.invoke({"messages": messages})

    # Extract the last AI message from the agent's response
    ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
    if ai_messages:
        response = ai_messages[-1]
    else:
        response = AIMessage(content="I apologize, I wasn't able to process your product query. Could you please rephrase?")

    return {
        "messages": [response],
        "current_agent": "product",
    }
