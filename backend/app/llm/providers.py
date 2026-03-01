from __future__ import annotations

"""LLM provider configuration — Anthropic (Claude) and OpenAI (GPT)."""

import logging

from app.config import get_settings

logger = logging.getLogger(__name__)


def get_anthropic_llm(model_name: str = None):
    """Create and return a ChatAnthropic instance.

    Args:
        model_name: Override the model (e.g. 'claude-sonnet-4-20250514').
                    Defaults to settings.primary_llm.
    """
    from langchain_anthropic import ChatAnthropic

    settings = get_settings()
    return ChatAnthropic(
        model=model_name or settings.primary_llm,
        api_key=settings.anthropic_api_key,
        temperature=0.1,
        max_tokens=4096,
    )


def get_openai_llm(model_name: str = None):
    """Create and return a ChatOpenAI instance.

    Args:
        model_name: Override the model (e.g. 'gpt-4o', 'gpt-4o-mini').
                    Defaults to settings.primary_llm.
    """
    from langchain_openai import ChatOpenAI

    settings = get_settings()
    return ChatOpenAI(
        model=model_name or settings.primary_llm,
        temperature=0.1,
        max_tokens=4096,
        api_key=settings.openai_api_key,
    )
