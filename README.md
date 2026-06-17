# NemoDesk — Enterprise IT Ticket AI

**Agentic IT service-desk automation built on the [NVIDIA NeMo Agent Toolkit](https://github.com/NVIDIA/NeMo-Agent-Toolkit) (NemoClaw), powered by NVIDIA Nemotron NIMs.**

> Submission for the **India Agentic AI Open Hackathon** (NVIDIA + gnani.ai) — **Track A: Agentic Workflows**.

NemoDesk turns a raw IT support ticket into a triaged, prioritized, runbook-grounded, and (where possible) auto-resolved outcome using a team of cooperating agents — with PII redaction, SLA routing, and an ITSM system of record built in.

---

## Why NemoDesk

Enterprise IT service desks are drowning: high ticket volume, inconsistent triage, slow first response, and L1 agents copy-pasting from scattered runbooks. NemoDesk applies an **agentic workflow** to the entire first-touch lifecycle:

| Problem | NemoDesk |
|---|---|
| Manual, inconsistent triage | LLM classifier → category + P1–P4 priority with rationale |
| Sensitive data sent to models | Deterministic PII/secret redaction **before** any LLM call |
| Slow routing & SLA breaches | Automated team routing + SLA due-time computation |
| Tribal-knowledge resolutions | RAG over approved runbooks grounds every answer |
| No system of record | ITSM connector persists an auditable ticket record |

## Architecture

```
                     Incoming ticket (REST / nat run / UI)
                                   │
                  ┌────────────────▼─────────────────┐
                  │  Supervisor  (react_agent)        │
                  │  LLM: nvidia/nemotron-3-nano      │
                  └───────┬───────────────┬───────────┘
                          │               │
            ┌─────────────▼───┐     ┌─────▼──────────────┐
            │  triage_agent   │     │ resolution_agent   │
            │ (tool_calling)  │     │ (tool_calling)     │
            ├─────────────────┤     ├────────────────────┤
            │ pii_redactor    │     │ kb_search (RAG)    │
            │ ticket_classifier│    │ itsm_connector     │
            │ escalation_router│    │                    │
            └─────────────────┘     └────────────────────┘
                          │               │
                 category, priority,   runbook steps,
                 team, SLA             ITSM ticket id
```

Two `tool_calling_agent` experts coordinated by a `react_agent` supervisor — the
canonical NeMo Agent Toolkit multi-agent pattern.

### Custom tools (NAT plugin `nemodesk`)

| Tool | Type | What it does |
|---|---|---|
| `pii_redactor` | deterministic | Masks emails, IPs, phones, card numbers, secrets before any LLM call |
| `ticket_classifier` | LLM (Nemotron) | Category + P1–P4 priority + confidence, with keyword fallback |
| `kb_search` | RAG (NIM embedder) | Semantic search over approved markdown runbooks |
| `escalation_router` | deterministic | Maps category→owning team and computes SLA due time |
| `itsm_connector` | connector | Persists a ServiceNow/Jira-style ticket (mock JSONL store; swap for real REST) |

## Quickstart

### 1. Install

```bash
git clone https://github.com/Yash-Kavaiya/nemodesk-it-agent.git
cd nemodesk-it-agent
uv venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install .                              # installs nvidia-nat[langchain] + fastapi
```

### 2. Set your NVIDIA API key

Get a key at [build.nvidia.com](https://build.nvidia.com/), then:

```bash
export NVIDIA_API_KEY=nvapi-...
```

### 3. Run a single ticket

```bash
nat run --config_file configs/config.yml \
  --input "Outlook keeps crashing on launch after the latest Windows update on my laptop."
```

### 4. Serve the REST API

```bash
uvicorn api.server:app --host 0.0.0.0 --port 8080
# then:
curl -X POST localhost:8080/v1/tickets/resolve \
  -H 'Content-Type: application/json' \
  -d '{"text":"VPN is down for the whole office, production support blocked","external_id":"SNOW-123"}'
```

### 5. Launch the NeMo Agent Toolkit chat UI

```bash
nat serve --config_file configs/config.yml
# Connect the NeMo Agent Toolkit UI to the served endpoint.
```

### 6. Run on the batch demo

```bash
python scripts/demo_batch.py        # runs all 10 sample tickets
```

## Evaluation

NemoDesk ships an eval harness using RAGAS metrics judged by a Nemotron NIM:

```bash
nat eval --config_file configs/eval_config.yml
```

Dataset: `eval/eval_dataset.json` (10 labelled tickets across all categories).
Metrics: `AnswerAccuracy`, `ResponseGroundedness`.

## Docker

```bash
docker compose up --build      # requires NVIDIA_API_KEY in env or .env
curl localhost:8080/health
```

## Tests

```bash
pip install ".[dev]"
pytest -q                       # deterministic logic: PII, routing, SLA (no API key needed)
```

## Repo layout

```
configs/        config.yml (workflow) + eval_config.yml
src/nemodesk/   package: models, register (plugin entry point)
  tools/        pii_redactor, classifier, kb_search, escalation (+itsm)
data/           knowledge_base/*.md runbooks + sample_tickets.json
api/            FastAPI REST integration layer
eval/           eval dataset
scripts/        batch demo runner
docs/           ARCHITECTURE.md, PITCH_DECK.md
tests/          unit tests for deterministic logic
```

## Tech stack

- **NVIDIA NeMo Agent Toolkit** (`nvidia-nat`) — multi-agent orchestration, MCP/A2A ready
- **NVIDIA Nemotron NIMs** — `nvidia/nemotron-3-nano-30b-a3b` (reasoning) + `nv-embedqa-e5-v5` (embeddings)
- **LangChain/LangGraph** framework wrappers
- **FastAPI** for enterprise REST integration

## Roadmap

- MCP server exposure of NemoDesk tools for other agents to consume
- A2A protocol: NemoDesk as a distributed node in a larger ops mesh
- Real ServiceNow/Jira connectors behind `itsm_connector`
- RL fine-tuning of the classifier on historical resolved tickets (NeMo)
- Observability via Phoenix/LangSmith tracing (native NAT integration)

## License

Apache-2.0. Built on NVIDIA NeMo Agent Toolkit (Apache-2.0).
