from __future__ import annotations

"""Escalation agent — detects when human intervention is needed and prepares handoff."""

import logging

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agents.state import AgentState
from app.llm.fallback import get_llm

logger = logging.getLogger(__name__)

ESCALATION_SYSTEM_PROMPT = """You are an Escalation Handler for an e-commerce customer care system.

Your job is to:
1. Acknowledge the customer's frustration or request for human assistance
2. Summarize the conversation so far for the human agent who will take over
3. Provide a polite, empathetic response to the customer

Generate a response with TWO parts:

PART 1 - Customer-facing message:
- Acknowledge their request/frustration empathetically
- Let them know a human agent will be connected shortly
- Assure them their issue is important
- Mention that the human agent will have full context of the conversation

PART 2 - Internal handoff summary (prefix with "HANDOFF_SUMMARY:"):
- Brief description of the customer's issue
- What has been attempted so far
- Customer's emotional state
- Priority level (low/medium/high/urgent)

Format your response EXACTLY like this:
[Customer message here]

HANDOFF_SUMMARY: [Summary for human agent here]
"""


def escalation_agent_node(state: AgentState) -> dict:
    """LangGraph node function for the escalation agent.

    This agent does NOT use tools. It analyzes the conversation and
    generates a handoff summary for human agents.
    """
    logger.info("Escalation Agent handling query")

    llm = get_llm("escalation_agent")

    messages = [SystemMessage(content=ESCALATION_SYSTEM_PROMPT)] + list(state["messages"])

    response = llm.invoke(messages)

    # Parse the response to extract handoff summary
    content = response.content if isinstance(response, AIMessage) else str(response)
    escalation_reason = ""

    if "HANDOFF_SUMMARY:" in content:
        parts = content.split("HANDOFF_SUMMARY:")
        customer_message = parts[0].strip()
        escalation_reason = parts[1].strip()
    else:
        customer_message = content
        escalation_reason = "Customer requested human assistance"

    return {
        "messages": [AIMessage(content=customer_message)],
        "current_agent": "escalation",
        "escalation_needed": True,
        "escalation_reason": escalation_reason,
    }
