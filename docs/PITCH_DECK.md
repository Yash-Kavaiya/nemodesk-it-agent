# NemoDesk — Pitch Deck Outline

> India Agentic AI Open Hackathon (NVIDIA + gnani.ai) · Track A: Agentic Workflows
> Use this as the storyboard for the required submission deck.

---

### Slide 1 — Title
**NemoDesk: Enterprise IT Ticket AI**
Agentic IT service-desk automation on the NVIDIA NeMo Agent Toolkit (NemoClaw).
Team name · members · contact. Track A.

### Slide 2 — The Problem
- Enterprise service desks face high ticket volume and rising costs.
- First response is slow; triage is inconsistent; SLAs get breached.
- L1 agents hunt through scattered runbooks; resolutions are tribal knowledge.
- Sensitive data routinely lands in tickets (emails, IPs, credentials).

### Slide 3 — The Opportunity
- 60–80% of L1 tickets are repetitive and runbook-resolvable.
- Agentic AI can own the entire first touch: triage → route → resolve → record.
- Quantify: target X% auto-resolution, Y-minute first response, Z% SLA adherence.

### Slide 4 — Solution: NemoDesk
A team of cooperating agents that takes a raw ticket and returns:
category · priority (P1–P4) · owning team · SLA · runbook-grounded steps · ITSM id.
PII is redacted before any model sees it.

### Slide 5 — Architecture (diagram)
Supervisor `react_agent` → `triage_agent` + `resolution_agent`.
5 custom tools: pii_redactor, ticket_classifier, kb_search (RAG), escalation_router,
itsm_connector. (Use the diagram from docs/ARCHITECTURE.md.)

### Slide 6 — NVIDIA Stack
- NeMo Agent Toolkit for multi-agent orchestration, eval, observability.
- Nemotron NIM (`nemotron-3-nano-30b-a3b`) for reasoning + tool use.
- `nv-embedqa-e5-v5` for RAG embeddings.
- MCP / A2A ready; NIM-portable (cloud or on-prem).

### Slide 7 — Live Demo
1. P1 outage ticket → instant triage, routed to Network-Ops, SLA 15 min.
2. Phishing ticket with credentials → PII redacted, escalated to SecOps as P1.
3. Outlook crash → RAG pulls RB-001, returns numbered fix, records INC ticket.
Show `nat run`, the REST call, and the ITSM store entry.

### Slide 8 — Enterprise-Grade by Design
- PII/secret redaction at the boundary (deterministic, pre-LLM).
- Grounded answers (RAG over approved runbooks — no hallucinated fixes).
- Deterministic SLA + routing tables (testable, predictable).
- Auditable system of record; graceful fallback if a model call fails.

### Slide 9 — Evaluation
- `nat eval` with RAGAS (AnswerAccuracy, ResponseGroundedness), Nemotron as judge.
- 10-ticket labelled dataset across all categories.
- Report accuracy / groundedness numbers from your run here.

### Slide 10 — Impact & ROI
- Deflected tickets × avg handle time × loaded agent cost = $ saved.
- Faster MTTR, fewer SLA breaches, consistent quality, 24/7 coverage.

### Slide 11 — Roadmap
MCP server exposure · A2A mesh · real ServiceNow/Jira connectors ·
RL fine-tuning of the classifier on historical tickets · Phoenix/LangSmith tracing.

### Slide 12 — Ask / Close
What we need (compute, mentorship, pilot data). Repo + contact.
**github.com/Yash-Kavaiya/nemodesk-it-agent**
