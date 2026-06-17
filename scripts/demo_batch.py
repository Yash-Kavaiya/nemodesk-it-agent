# SPDX-License-Identifier: Apache-2.0
"""Batch demo runner for NemoDesk.

Loads the NeMo Agent Toolkit workflow once and runs every ticket in
data/sample_tickets.json through it, printing the agentic result for each.

Usage:
    export NVIDIA_API_KEY=***    python scripts/demo_batch.py [path/to/config.yml]
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "configs" / "config.yml")
TICKETS = ROOT / "data" / "sample_tickets.json"


async def main() -> None:
    from nat.runtime.loader import load_workflow

    tickets = json.loads(TICKETS.read_text(encoding="utf-8"))
    print(f"NemoDesk batch demo — {len(tickets)} tickets — config={CONFIG}\n")

    async with load_workflow(CONFIG) as session_manager:
        for t in tickets:
            print("=" * 78)
            print(f"[{t['id']}] {t['text']}")
            print(f"  expected: {t['expected_category']} / {t['expected_priority']}")
            try:
                async with session_manager.session() as session:
                    async with session.run(t["text"]) as runner:
                        result = await runner.result(to_type=str)
                print("  --- NemoDesk result ---")
                print("  " + result.replace("\n", "\n  "))
            except Exception as exc:  # noqa: BLE001
                print(f"  ERROR: {exc}")
            print()


if __name__ == "__main__":
    asyncio.run(main())
