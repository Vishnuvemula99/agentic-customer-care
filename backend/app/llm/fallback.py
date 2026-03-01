from __future__ import annotations

"""LLM selection with automatic fallback — supports Anthropic and OpenAI."""

import logging

from app.config import get_settings
from app.llm.providers import get_anthropic_llm, get_openai_llm

logger = logging.getLogger(__name__)


def get_llm_with_fallback():
    """Get the primary LLM with automatic fallback to the secondary.

    Detects which API keys are configured and builds a fallback chain.
    Supports: OpenAI (GPT), Anthropic (Claude), or both.
    """
    settings = get_settings()

    has_anthropic = (
        settings.anthropic_api_key
        and settings.anthropic_api_key != "your-anthropic-key-here"
    )
    has_openai = (
        settings.openai_api_key
        and settings.openai_api_key != "your-openai-key-here"
    )

    if has_anthropic and has_openai:
        primary = get_anthropic_llm(settings.primary_llm)
        fallback = get_openai_llm(settings.fallback_llm)
        logger.info(
            f"LLM: primary={settings.primary_llm} (Anthropic), "
            f"fallback={settings.fallback_llm} (OpenAI)"
        )
        return primary.with_fallbacks([fallback])

    elif has_openai:
        primary = get_openai_llm(settings.primary_llm)
        # Add fallback if a different model is configured
        if settings.fallback_llm and settings.fallback_llm != settings.primary_llm:
            fallback = get_openai_llm(settings.fallback_llm)
            logger.info(
                f"LLM: primary={settings.primary_llm}, fallback={settings.fallback_llm}"
            )
            return primary.with_fallbacks([fallback])
        logger.info(f"LLM: model={settings.primary_llm}")
        return primary

    elif has_anthropic:
        logger.info(f"LLM: model={settings.primary_llm} (Anthropic)")
        return get_anthropic_llm(settings.primary_llm)

    else:
        raise ValueError(
            "No LLM configured. Set at least one API key in .env:\n"
            "  OPENAI_API_KEY=sk-...\n"
            "  ANTHROPIC_API_KEY=sk-ant-..."
        )


def get_llm(agent_name: str = "default"):
    """Get the appropriate LLM for an agent.

    Args:
        agent_name: Identifier for the agent requesting the LLM, used in
            log messages for debugging.
    """
    try:
        return get_llm_with_fallback()
    except Exception as e:
        logger.error(f"Failed to initialize LLM for {agent_name}: {e}")
        raise
