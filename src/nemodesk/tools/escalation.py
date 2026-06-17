# SPDX-License-Identifier: Apache-2.0
"""Escalation router + mock ITSM connector.

`escalation_router` maps a classified ticket to the owning fulfilment team and
computes the SLA due time. `itsm_connector` simulates creating/updating a ticket
in an ITSM system (ServiceNow / Jira style) and persists it to a local JSONL store
so the demo is fully runnable without external credentials. Swap the persistence
body for a real REST call in production.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from nat.builder.builder import Builder
from nat.builder.function_info import FunctionInfo
from nat.cli.register_workflow import register_function
from nat.data_models.function import FunctionBaseConfig

from nemodesk.models import ROUTING_TABLE, SLA_MINUTES, Priority

logger = logging.getLogger(__name__)


class EscalationRouterConfig(FunctionBaseConfig, name="escalation_router"):
    """Route a ticket to the correct team and compute its SLA."""


@register_function(config_type=EscalationRouterConfig)
async def escalation_router(config: EscalationRouterConfig, builder: Builder):

    async def _route(category: str, priority: str) -> str:
        """Given a category and priority, return owning team + SLA due timestamp as JSON."""
        team = ROUTING_TABLE.get(category, "Service-Desk-L1")
        sla_min = SLA_MINUTES.get(priority, SLA_MINUTES[Priority.P3.value])
        due = datetime.now(timezone.utc) + timedelta(minutes=sla_min)
        return json.dumps({
            "assigned_team": team,
            "priority": priority,
            "sla_minutes": sla_min,
            "sla_due_utc": due.isoformat(),
        })

    yield FunctionInfo.from_fn(
        _route,
        description=("Route a ticket to the owning team and compute SLA. "
                     "Inputs: category, priority. Output: JSON with assigned_team and sla_due_utc."),
    )


class ItsmConnectorConfig(FunctionBaseConfig, name="itsm_connector"):
    """Create/update a ticket record in a (mock) ITSM backend."""

    store_path: str = "data/itsm_store.jsonl"


@register_function(config_type=ItsmConnectorConfig)
async def itsm_connector(config: ItsmConnectorConfig, builder: Builder):
    store = Path(config.store_path)
    store.parent.mkdir(parents=True, exist_ok=True)

    async def _create(summary: str, category: str, priority: str,
                      assigned_team: str, resolution: str = "") -> str:
        """Persist a ticket to the ITSM system. Returns the created ticket id + record as JSON."""
        ticket_id = f"INC{uuid.uuid4().hex[:8].upper()}"
        record = {
            "ticket_id": ticket_id,
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "summary": summary,
            "category": category,
            "priority": priority,
            "assigned_team": assigned_team,
            "resolution": resolution,
            "status": "Resolved" if resolution else "Assigned",
        }
        with store.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
        logger.info("ITSM connector wrote %s (%s)", ticket_id, record["status"])
        return json.dumps(record)

    yield FunctionInfo.from_fn(
        _create,
        description=("Create or update an ITSM ticket record (ServiceNow/Jira-style). "
                     "Inputs: summary, category, priority, assigned_team, resolution. "
                     "Output: JSON of the persisted ticket including ticket_id."),
    )
