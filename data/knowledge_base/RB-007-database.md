# Runbook RB-007: Database Performance / Connectivity

Category: database
Symptoms: Slow queries, deadlocks, connection pool exhaustion, replication lag.

## Resolution Steps
1. Identify blocking sessions / long-running queries (e.g. pg_stat_activity).
2. Check connection pool saturation and raise/limit as appropriate.
3. Review recent query/plan changes; check for missing indexes.
4. For deadlocks, capture the deadlock graph and identify contending transactions.
5. Replication lag: check WAL/redo shipping and network between primary and replica.

## Escalation
Data integrity risk or primary outage -> escalate to DBA-Team immediately as P1.
