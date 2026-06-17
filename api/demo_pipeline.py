# SPDX-License-Identifier: Apache-2.0
"""Deterministic demo pipeline for NemoDesk.

Reproduces the agentic outcome (PII redaction -> classification -> routing -> SLA
-> runbook lookup -> ITSM record) using ONLY the deterministic logic that backs
the real tools, so the UI works end-to-end with no NVIDIA_API_KEY. The production
path (NVIDIA NIM + RAG) lives in the NeMo Agent Toolkit workflow; this module is a
faithful, offline approximation used for the demo endpoint.
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from nemodesk.models import ROUTING_TABLE, SLA_MINUTES, Category, Priority

# NOTE: the keyword map and PII patterns below mirror the deterministic logic in
# nemodesk.tools.classifier and nemodesk.tools.pii_redactor. They are duplicated
# here (rather than imported) so the demo endpoint works WITHOUT installing the
# full nvidia-nat stack, which those tool modules import at module load time.
_KEYWORDS: dict[Category, list[str]] = {
    Category.SECURITY: ["phishing", "malware", "breach", "ransomware", "suspicious", "compromised", "fake site", "fake page"],
    Category.ACCESS: ["password", "login", "locked out", "mfa", "access", "permission", "vpn account", "reset"],
    Category.NETWORK: ["wifi", "network", "vpn", "dns", "latency", "packet", "firewall", "connectivity"],
    Category.HARDWARE: ["laptop", "monitor", "keyboard", "printer", "battery", "screen", "dock", "power on"],
    Category.EMAIL: ["outlook", "email", "mailbox", "calendar", "teams", "smtp"],
    Category.CLOUD: ["aws", "azure", "gcp", "ec2", "s3", "kubernetes", "pod", "cluster", "crashloopbackoff"],
    Category.DATABASE: ["sql", "database", "query", "deadlock", "replication", "postgres", "oracle"],
    Category.SOFTWARE: ["install", "crash", "license", "update", "application", "error code"],
}

_PATTERNS: list[tuple[str, "re.Pattern"]] = [
    ("[EMAIL]", re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")),
    ("[IP]", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
    ("[PHONE]", re.compile(r"\b(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)\d{3}[\s-]?\d{4}\b")),
    ("[CARD]", re.compile(r"\b(?:\d[ -]*?){13,16}\b")),
    ("[SECRET]", re.compile(r"(?i)(password|passwd|pwd|token|api[_-]?key|secret)\s*[:=]\s*\S+")),
]

# Map each category to its canonical runbook id (matches data/knowledge_base).
_RUNBOOK = {
    Category.EMAIL.value: "RB-001-outlook-crash.md",
    Category.NETWORK.value: "RB-002-vpn-connectivity.md",
    Category.ACCESS.value: "RB-003-password-reset.md",
    Category.HARDWARE.value: "RB-004-laptop-hardware.md",
    Category.SECURITY.value: "RB-005-phishing-incident.md",
    Category.CLOUD.value: "RB-006-cloud-k8s.md",
    Category.DATABASE.value: "RB-007-database.md",
    Category.SOFTWARE.value: "RB-008-software-install.md",
    Category.OTHER.value: None,
}

_P1_WORDS = ["down", "outage", "critical", "cannot work", "production", "all users", "whole office", "everyone"]


def _redact(text: str) -> tuple[str, int]:
    out, hits = text, 0
    for token, pattern in _PATTERNS:
        out, n = pattern.subn(token, out)
        hits += n
    return out, hits


def _classify(text: str) -> tuple[str, str]:
    low = text.lower()
    category = Category.OTHER.value
    for cat, words in _KEYWORDS.items():
        if any(w in low for w in words):
            category = cat.value
            break
    if category == Category.SECURITY.value:
        priority = Priority.P1.value
    elif any(w in low for w in _P1_WORDS):
        priority = Priority.P1.value
    elif category in (Category.HARDWARE.value, Category.DATABASE.value, Category.NETWORK.value):
        priority = Priority.P2.value
    else:
        priority = Priority.P3.value
    return category, priority


def _runbook_steps(kb_dir: Path, category: str) -> tuple[str, list[str]]:
    rb = _RUNBOOK.get(category)
    if not rb:
        return "", []
    path = kb_dir / rb
    if not path.exists():
        return rb, []
    steps: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*\d+\.\s+(.*)", line)
        if m:
            steps.append(m.group(1).strip())
    return rb, steps


def run_demo(text: str, kb_dir: str = "data/knowledge_base", external_id: str | None = None) -> dict:
    """Run the deterministic pipeline and return a structured result for the UI."""
    redacted, pii_hits = _redact(text)
    category, priority = _classify(text)
    team = ROUTING_TABLE.get(category, "Service-Desk-L1")
    sla_min = SLA_MINUTES.get(priority, SLA_MINUTES[Priority.P3.value])
    due = datetime.now(timezone.utc) + timedelta(minutes=sla_min)
    runbook, steps = _runbook_steps(Path(kb_dir), category)

    is_security = category == Category.SECURITY.value
    escalated = is_security or priority == Priority.P1.value
    ticket_id = f"INC{uuid.uuid4().hex[:8].upper()}"

    return {
        "external_id": external_id,
        "ticket_id": ticket_id,
        "redacted_text": redacted,
        "pii_redacted": pii_hits,
        "category": category,
        "priority": priority,
        "assigned_team": team,
        "sla_minutes": sla_min,
        "sla_due_utc": due.isoformat(),
        "runbook": runbook,
        "resolution_steps": steps,
        "escalated": escalated,
        "status": "Escalated" if escalated else ("Resolved" if steps else "Assigned"),
        "engine": "demo (deterministic, no LLM)",
    }
