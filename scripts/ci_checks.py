# SPDX-License-Identifier: Apache-2.0
"""Dependency-light CI checks for NemoDesk deterministic logic.

Validates PII redaction patterns, routing-table coverage and SLA ordering WITHOUT
installing the full nvidia-nat stack (so CI is fast and needs no NVIDIA_API_KEY).
Loads models.py directly and extracts the _PATTERNS literal from pii_redactor.py.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_models():
    spec = importlib.util.spec_from_file_location("nd_models", ROOT / "src/nemodesk/models.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_patterns():
    src = (ROOT / "src/nemodesk/tools/pii_redactor.py").read_text(encoding="utf-8")
    start = src.index("_PATTERNS")
    block = src[start:src.index("]\n", start) + 1]
    ns: dict = {"re": re}
    exec(block, ns)  # noqa: S102 - trusted local source
    return ns["_PATTERNS"]


def redact(text: str, patterns) -> str:
    for token, pattern in patterns:
        text = pattern.sub(token, text)
    return text


def main() -> int:
    m = _load_models()
    patterns = _load_patterns()
    failures = []

    def check(name, cond):
        print(("PASS" if cond else "FAIL"), name)
        if not cond:
            failures.append(name)

    check("email redaction", "[EMAIL]" in redact("contact a@b.com", patterns))
    check("ip redaction", "[IP]" in redact("host 10.0.0.1", patterns))
    check("secret redaction", "[SECRET]" in redact("api_key=xyz", patterns))
    check("routing covers all categories", all(c.value in m.ROUTING_TABLE for c in m.Category))
    check("sla ordering", m.SLA_MINUTES["P1"] < m.SLA_MINUTES["P2"] < m.SLA_MINUTES["P3"] < m.SLA_MINUTES["P4"])

    print("\nRESULT:", "ALL PASS" if not failures else f"FAILED: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
