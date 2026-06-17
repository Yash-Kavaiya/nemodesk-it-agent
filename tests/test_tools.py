# SPDX-License-Identifier: Apache-2.0
"""Unit tests for NemoDesk deterministic logic (no LLM / network required).

These cover the PII redactor, the keyword classifier fallback, and the routing /
SLA tables, so CI can validate the core safety + routing behaviour without an
NVIDIA_API_KEY.
"""

import re

import pytest

from nemodesk.models import ROUTING_TABLE, SLA_MINUTES, Category, Priority
from nemodesk.tools.pii_redactor import _PATTERNS


def _redact(text: str) -> str:
    out = text
    for token, pattern in _PATTERNS:
        out = pattern.sub(token, out)
    return out


def test_email_redaction():
    assert "[EMAIL]" in _redact("contact john.doe@acme.com please")
    assert "@acme.com" not in _redact("john.doe@acme.com")


def test_ip_redaction():
    assert "[IP]" in _redact("replica 10.2.4.19 is lagging")


def test_secret_redaction():
    assert "Summer2026" not in _redact("password: Summer2026!")
    assert "[SECRET]" in _redact("api_key=abcd1234")


def test_routing_table_covers_all_categories():
    for cat in Category:
        assert cat.value in ROUTING_TABLE, f"missing routing for {cat}"


def test_sla_priority_ordering():
    # Higher severity must have a tighter (smaller) SLA.
    assert SLA_MINUTES[Priority.P1.value] < SLA_MINUTES[Priority.P2.value]
    assert SLA_MINUTES[Priority.P2.value] < SLA_MINUTES[Priority.P3.value]
    assert SLA_MINUTES[Priority.P3.value] < SLA_MINUTES[Priority.P4.value]


@pytest.mark.parametrize("text,expected", [
    ("phishing email asking for my password", Category.SECURITY),
    ("vpn keeps dropping", Category.NETWORK),
    ("laptop won't power on", Category.HARDWARE),
])
def test_keyword_heuristic(text, expected):
    # Import the heuristic logic indirectly via keyword map.
    from nemodesk.tools.classifier import _KEYWORDS
    low = text.lower()
    matched = [cat for cat, words in _KEYWORDS.items() if any(w in low for w in words)]
    assert expected in matched
