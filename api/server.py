# SPDX-License-Identifier: Apache-2.0
"""NemoDesk REST API.

A thin enterprise-integration layer over the NeMo Agent Toolkit workflow. ITSM
systems (ServiceNow, Jira, Zendesk) POST a ticket here and receive the agentic
triage + resolution result. The SessionManager is loaded once from
configs/config.yml; each request opens a short-lived session.

Run:
    export NVIDIA_API_KEY=***    uvicorn api.server:app --host 0.0.0.0 --port 8080

Note: NeMo Agent Toolkit also exposes its own server via `nat serve`. This module
shows how to embed the workflow in a custom FastAPI service for full control over
the request/response contract and auth.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

CONFIG_FILE = os.environ.get("NEMODESK_CONFIG", "configs/config.yml")

# Populated at startup.
_ctx: dict = {"session_manager": None, "load_error": None, "_cm": None}


class TicketRequest(BaseModel):
    text: str = Field(..., description="Raw ticket text submitted by the end user")
    source: str = Field("api", description="Originating system, e.g. servicenow/jira")
    external_id: str | None = Field(None, description="Caller's own ticket id, for correlation")


class TicketResponse(BaseModel):
    external_id: str | None
    result: str
    engine: str = "nemo-agent-toolkit"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the NAT SessionManager once at startup; tear it down on shutdown."""
    try:
        from nat.runtime.loader import load_workflow

        cm = load_workflow(CONFIG_FILE)
        session_manager = await cm.__aenter__()
        _ctx["session_manager"] = session_manager
        _ctx["_cm"] = cm
    except Exception as exc:  # noqa: BLE001
        # Defer the error to request time so /health still works for diagnostics.
        _ctx["load_error"] = str(exc)
    yield
    cm = _ctx.get("_cm")
    if cm is not None:
        await cm.__aexit__(None, None, None)


app = FastAPI(
    title="NemoDesk IT Ticket AI",
    description="Enterprise IT ticket resolution agentic system on the NVIDIA NeMo Agent Toolkit.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "config": CONFIG_FILE,
        "workflow_loaded": _ctx["session_manager"] is not None,
        "load_error": _ctx["load_error"],
        "nvidia_api_key_set": bool(os.environ.get("NVIDIA_API_KEY")),
    }


@app.post("/v1/tickets/resolve", response_model=TicketResponse)
async def resolve_ticket(req: TicketRequest):
    session_manager = _ctx["session_manager"]
    if session_manager is None:
        raise HTTPException(
            status_code=503,
            detail=f"Workflow not loaded: {_ctx['load_error'] or 'unknown error'}",
        )
    try:
        async with session_manager.session() as session:
            async with session.run(req.text) as runner:
                result = await runner.result(to_type=str)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Workflow error: {exc}") from exc

    return TicketResponse(external_id=req.external_id, result=result)


@app.post("/v1/tickets/demo")
async def demo_ticket(req: TicketRequest):
    """Deterministic, offline demo of the agentic pipeline (no NVIDIA_API_KEY needed).

    Powers the UI's demo mode and is always available. Returns a structured result
    (category, priority, team, SLA, runbook steps, ITSM id) so the UI can render the
    full outcome even without a configured NIM endpoint.
    """
    from api.demo_pipeline import run_demo

    kb_dir = os.environ.get("NEMODESK_KB_DIR", "data/knowledge_base")
    try:
        return run_demo(req.text, kb_dir=kb_dir, external_id=req.external_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Demo pipeline error: {exc}") from exc


# ---- Static UI (served at /) ----
_UI_DIR = Path(__file__).resolve().parent / "ui"


@app.get("/", include_in_schema=False)
async def ui_index():
    index = _UI_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    raise HTTPException(status_code=404, detail="UI not found")


if _UI_DIR.exists():
    app.mount("/ui", StaticFiles(directory=str(_UI_DIR), html=True), name="ui")

