# NemoDesk Architecture

## 1. Overview

NemoDesk is a multi-agent system that automates the first-touch lifecycle of an
enterprise IT support ticket. It is implemented entirely on the **NVIDIA NeMo
Agent Toolkit** (`nvidia-nat`, a.k.a. "NemoClaw") and uses **NVIDIA Nemotron
NIMs** for reasoning and embeddings.

## 2. Agent topology

NemoDesk uses the toolkit's **supervisor + expert-agents** pattern:

- **Supervisor** — a `react_agent` that reasons (Thought/Action/Observation) about
  which expert to invoke and in what order, then composes the final answer.
- **triage_agent** — a `tool_calling_agent` that owns *understanding* the ticket.
- **resolution_agent** — a `tool_calling_agent` that owns *resolving* the ticket.

Each expert agent is itself exposed to the supervisor as a callable "tool", so the
supervisor delegates naturally. This keeps each agent's prompt and tool surface
small, which improves reliability and token efficiency on small Nemotron models.

## 3. Request flow

```
1. Ticket text arrives (REST /v1/tickets/resolve, `nat run`, or UI).
2. Supervisor → triage_agent:
     a. pii_redactor      : strip emails/IPs/phones/cards/secrets (deterministic)
     b. ticket_classifier : Nemotron → {category, priority, confidence, rationale}
     c. escalation_router : {assigned_team, sla_minutes, sla_due_utc}
3. Supervisor → resolution_agent:
     a. kb_search         : RAG over runbooks (NIM embedder + USearch vector store)
     b. itsm_connector    : persist {ticket_id, category, priority, team, resolution}
4. Supervisor composes final answer:
     category · priority · team · SLA · ITSM id · numbered resolution steps
     (security incidents and unresolved tickets are flagged as escalated)
```

## 4. Safety & enterprise concerns

- **PII never reaches the model.** `pii_redactor` is deterministic regex run before
  any LLM invocation, so emails, IPs, phone numbers, card-like numbers and
  credentials are masked at the boundary.
- **Grounded resolutions.** Resolution steps are retrieved from an approved runbook
  corpus via RAG rather than hallucinated.
- **Auditable.** Every processed ticket is written to the ITSM store with a unique
  `INC########` id, category, priority, owning team and resolution.
- **Graceful degradation.** The classifier falls back to a deterministic keyword +
  severity heuristic if the model output can't be parsed, so the pipeline never
  hard-fails on classification.
- **Deterministic SLA.** Priority→SLA and category→team are explicit tables
  (`models.py`), not model guesses, so routing is predictable and testable.

## 5. Models

| Role | Model | Why |
|---|---|---|
| Supervisor reasoning | `nvidia/nemotron-3-nano-30b-a3b` | Strong tool-use reasoning, efficient |
| Worker / tool agents | `nvidia/nemotron-3-nano-30b-a3b` | temp=0 for deterministic tool calls |
| Embeddings (RAG) | `nvidia/nv-embedqa-e5-v5` | High-quality retrieval embeddings |

All served via NVIDIA NIM (`build.nvidia.com`). Swap `_type: nim` for a local NIM
container or another provider without changing tool code.

## 6. Extensibility

- **MCP**: expose NemoDesk tools as an MCP server (`nat mcp` / FastMCP) for reuse.
- **A2A**: register NemoDesk as a distributed agent node.
- **Real ITSM**: replace the body of `itsm_connector._create` with a ServiceNow/
  Jira REST call; the contract (inputs/outputs) stays identical.
- **Fine-tuning**: use NeMo RL to train the classifier on historical tickets.
- **Observability**: enable native LangSmith/Phoenix tracing in NAT config.

## 7. Why the NeMo Agent Toolkit

- Framework-agnostic instrumentation, profiling, and evaluation out of the box.
- First-class multi-agent composition (`react_agent`, `tool_calling_agent`).
- Native NIM/Nemotron integration and MCP/A2A protocol support.
- Built-in evaluation (`nat eval`) and optimization tooling.
