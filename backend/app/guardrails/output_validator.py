from __future__ import annotations

"""Output validation guardrails — validate agent responses before sending to users."""

import logging
import re

logger = logging.getLogger(__name__)

# Prohibited content patterns
PROHIBITED_PATTERNS = [
    (r"(?i)i am not (a|an) (ai|robot|bot|machine)", "identity_denial"),
    (r"(?i)this is (not )?legal advice", "legal_advice"),
    (r"(?i)i (guarantee|promise) (that |)(delivery|it will arrive)", "false_promise"),
    (r"(?i)(sue|lawsuit|legal action|attorney|lawyer)", "legal_reference"),
    (r"(?i)competitor[s]?\s+(like|such as|including)\s+\w+", "competitor_mention"),
]

_compiled_prohibited = [
    (re.compile(pattern), label) for pattern, label in PROHIBITED_PATTERNS
]

# PII patterns for redaction
PII_PATTERNS = {
    "credit_card": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "phone": re.compile(r"\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
}


def validate_output(response: str, agent: str) -> tuple[str, list[str]]:
    """Validate an agent's response for policy compliance.

    Args:
        response: The agent's response text.
        agent: Which agent generated the response.

    Returns:
        Tuple of (validated_response, warnings). Response may be modified.
        Warnings are for logging only, not shown to users.
    """
    warnings = []

    if not response:
        return "I apologize, but I wasn't able to generate a response. Could you please rephrase your question?", []

    validated = response

    # Check for prohibited content
    for pattern, label in _compiled_prohibited:
        if pattern.search(validated):
            warnings.append(f"Prohibited content detected: {label}")
            logger.warning(f"Output guardrail triggered: {label} in {agent} response")

    # Redact any PII that might have leaked into the response
    for pii_type, pattern in PII_PATTERNS.items():
        if pattern.search(validated):
            validated = pattern.sub("[REDACTED]", validated)
            warnings.append(f"PII redacted from response: {pii_type}")
            logger.warning(f"PII ({pii_type}) found in {agent} response, redacted")

    # Agent-specific validation
    if agent == "returns":
        validated = _validate_returns_response(validated, warnings)

    return validated, warnings


def _validate_returns_response(response: str, warnings: list[str]) -> str:
    """Extra validation for returns agent — ensure no unauthorized promises."""
    # Check for refund promises without eligibility check references
    refund_promise = re.search(
        r"(?i)(your refund|refund of|we.ll refund|refund.*approved)", response
    )
    eligibility_ref = re.search(
        r"(?i)(eligib|policy|return window|within \d+ days)", response
    )

    if refund_promise and not eligibility_ref:
        warnings.append("Returns agent made refund promise without policy reference")
        response += "\n\n*Please note: All returns are subject to our return policy and eligibility requirements.*"

    return response
