# SPDX-License-Identifier: Apache-2.0
"""PII redaction tool - deterministic, runs before any ticket text reaches an LLM.

Enterprise requirement: tickets routinely contain emails, phone numbers, IPs,
credit-card-like numbers and credentials. We strip them with regex (no model call)
so sensitive data is never sent to an external NIM endpoint.
"""

from __future__ import annotations

import logging
import re

from nat.builder.builder import Builder
from nat.builder.function_info import FunctionInfo
from nat.cli.register_workflow import register_function
from nat.data_models.function import FunctionBaseConfig

logger = logging.getLogger(__name__)

_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("[EMAIL]", re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")),
    ("[IP]", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
    ("[PHONE]", re.compile(r"\b(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)\d{3}[\s-]?\d{4}\b")),
    ("[CARD]", re.compile(r"\b(?:\d[ -]*?){13,16}\b")),
    ("[SECRET]", re.compile(r"(?i)(password|passwd|pwd|token|api[_-]?key|secret)\s*[:=]\s*\S+")),
]


class PiiRedactorConfig(FunctionBaseConfig, name="pii_redactor"):
    """Redact PII/secrets from free text before it reaches an LLM."""


@register_function(config_type=PiiRedactorConfig)
async def pii_redactor(config: PiiRedactorConfig, builder: Builder):

    async def _redact(text: str) -> str:
        """Redact emails, IPs, phone numbers, card numbers and secrets from `text`."""
        redacted = text
        hits = 0
        for token, pattern in _PATTERNS:
            redacted, n = pattern.subn(token, redacted)
            hits += n
        logger.info("PII redactor masked %d sensitive span(s)", hits)
        return redacted

    yield FunctionInfo.from_fn(
        _redact,
        description=(
            "Redact personally identifiable information and secrets (emails, IPs, "
            "phone numbers, card numbers, passwords/tokens) from ticket text. "
            "Always call this before analyzing raw user-submitted text."
        ),
    )
