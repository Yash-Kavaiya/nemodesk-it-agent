# SPDX-License-Identifier: Apache-2.0
"""Ticket classification tool - LLM-backed category + priority detection.

Uses a NeMo Agent Toolkit-managed LLM (Nemotron NIM by default) to classify a
ticket into a category and SLA priority, returning structured JSON. A keyword
heuristic provides a deterministic fallback if the model output cannot be parsed,
so the workflow never hard-fails on a classification step.
"""

from __future__ import annotations

import json
import logging
import re

from nat.builder.builder import Builder
from nat.builder.framework_enum import LLMFrameworkEnum
from nat.builder.function_info import FunctionInfo
from nat.cli.register_workflow import register_function
from nat.data_models.component_ref import LLMRef
from nat.data_models.function import FunctionBaseConfig

from nemodesk.models import Category, Priority

logger = logging.getLogger(__name__)

_PROMPT = """You are an expert IT service-desk triage engine. Classify the ticket below.

Return ONLY a compact JSON object with these keys:
- "category": one of {categories}
- "priority": one of P1 (critical/business-down), P2 (high), P3 (medium), P4 (low/request)
- "confidence": float 0-1
- "rationale": one short sentence

Ticket:
\"\"\"{ticket}\"\"\"

JSON:"""

# Deterministic fallback keyword map.
_KEYWORDS: dict[Category, list[str]] = {
    Category.SECURITY: ["phishing", "malware", "breach", "ransomware", "suspicious", "compromised"],
    Category.ACCESS: ["password", "login", "locked out", "mfa", "access", "permission", "vpn account"],
    Category.NETWORK: ["wifi", "network", "vpn", "dns", "latency", "packet", "firewall", "connectivity"],
    Category.HARDWARE: ["laptop", "monitor", "keyboard", "printer", "battery", "screen", "dock"],
    Category.EMAIL: ["outlook", "email", "mailbox", "calendar", "teams", "smtp"],
    Category.CLOUD: ["aws", "azure", "gcp", "ec2", "s3", "kubernetes", "pod", "cluster"],
    Category.DATABASE: ["sql", "database", "query", "deadlock", "replication", "postgres", "oracle"],
    Category.SOFTWARE: ["install", "crash", "license", "update", "application", "error code"],
}


class TicketClassifierConfig(FunctionBaseConfig, name="ticket_classifier"):
    """Classify a ticket into category + SLA priority."""

    llm_name: LLMRef


@register_function(config_type=TicketClassifierConfig, framework_wrappers=[LLMFrameworkEnum.LANGCHAIN])
async def ticket_classifier(config: TicketClassifierConfig, builder: Builder):
    from langchain_core.language_models import BaseChatModel

    llm: BaseChatModel = await builder.get_llm(config.llm_name, wrapper_type=LLMFrameworkEnum.LANGCHAIN)
    categories = ", ".join(c.value for c in Category)

    def _heuristic(text: str) -> dict:
        low = text.lower()
        for cat, words in _KEYWORDS.items():
            if any(w in low for w in words):
                cat_val = cat.value
                break
        else:
            cat_val = Category.OTHER.value
        prio = Priority.P3.value
        if any(w in low for w in ["down", "outage", "critical", "cannot work", "production", "all users"]):
            prio = Priority.P1.value
        elif cat_val == Category.SECURITY.value:
            prio = Priority.P1.value
        return {"category": cat_val, "priority": prio, "confidence": 0.4,
                "rationale": "keyword heuristic fallback"}

    async def _classify(ticket: str) -> str:
        """Classify an IT ticket. Returns JSON: category, priority, confidence, rationale."""
        prompt = _PROMPT.format(categories=categories, ticket=ticket[:4000])
        try:
            resp = await llm.ainvoke(prompt)
            raw = resp.content if hasattr(resp, "content") else str(resp)
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            data = json.loads(match.group(0)) if match else _heuristic(ticket)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Classifier LLM parse failed (%s); using heuristic.", exc)
            data = _heuristic(ticket)

        # Validate against enums; fall back per-field.
        if data.get("category") not in {c.value for c in Category}:
            data["category"] = _heuristic(ticket)["category"]
        if data.get("priority") not in {p.value for p in Priority}:
            data["priority"] = Priority.P3.value
        return json.dumps(data)

    yield FunctionInfo.from_fn(
        _classify,
        description=(
            "Classify an IT support ticket. Input: the ticket text. "
            "Output: JSON with category, priority (P1-P4), confidence and rationale."
        ),
    )
