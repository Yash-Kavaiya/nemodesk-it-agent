# Runbook RB-005: Suspected Phishing / Security Incident

Category: security_incident
Symptoms: User reports a suspicious email, clicked a link, or entered credentials on a fake page.

## Resolution Steps (treat as P1)
1. Do NOT delete the email; preserve it for analysis.
2. If credentials were entered: immediately force a password reset and revoke active sessions/tokens.
3. Isolate the affected device from the network if malware execution is suspected.
4. Use the report-phishing button to submit to SecOps.
5. Check sign-in logs for anomalous locations/IPs.

## Escalation
ALWAYS escalate confirmed or suspected phishing to SecOps-CSIRT immediately as P1. Do not auto-close.
