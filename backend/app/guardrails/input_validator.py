from __future__ import annotations

"""Input validation guardrails — sanitize user messages before agent processing."""

import logging
import re

logger = logging.getLogger(__name__)

# Maximum message length
MAX_MESSAGE_LENGTH = 2000

# Prompt injection patterns
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)",
    r"you\s+are\s+now\s+(a|an)\s+",
    r"^system\s*:",
    r"forget\s+(everything|all|your)\s+(you|instructions|rules)",
    r"disregard\s+(all|your|previous)\s+(instructions|rules|guidelines)",
    r"pretend\s+you\s+are",
    r"act\s+as\s+(a|an|if)",
    r"override\s+(your|all|the)\s+(instructions|rules|guidelines)",
    r"new\s+instructions?\s*:",
    r"jailbreak",
    r"\[system\]",
    r"<\s*system\s*>",
]

# Compiled patterns for performance
_compiled_patterns = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


def validate_input(message: str) -> tuple[bool, str | None]:
    """Validate a user message for safety and length.

    Returns:
        Tuple of (is_valid, rejection_reason). If valid, rejection_reason is None.
    """
    if not message or not message.strip():
        return False, "Message cannot be empty."

    if len(message) > MAX_MESSAGE_LENGTH:
        return False, f"Message exceeds maximum length of {MAX_MESSAGE_LENGTH} characters."

    # Check for prompt injection
    for pattern in _compiled_patterns:
        if pattern.search(message):
            logger.warning(f"Prompt injection detected: pattern matched in message")
            return False, "I'm sorry, but I can only help with customer service queries about products, orders, and returns."

    return True, None


def sanitize_input(message: str) -> str:
    """Sanitize user input by stripping dangerous content."""
    # Strip HTML tags
    cleaned = re.sub(r"<[^>]+>", "", message)

    # Normalize whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # Truncate to max length
    if len(cleaned) > MAX_MESSAGE_LENGTH:
        cleaned = cleaned[:MAX_MESSAGE_LENGTH]

    return cleaned
