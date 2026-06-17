# Runbook RB-003: Account Lockout / Password Reset

Category: access_management
Symptoms: User locked out after failed logins, forgotten password, or expired credentials.

## Resolution Steps
1. Verify the user's identity per the identity-verification policy.
2. Unlock the account in the identity provider (Entra ID / AD).
3. Trigger a self-service password reset link, or set a temporary password requiring change at next logon.
4. Confirm MFA methods are still registered; re-enroll if needed.
5. Advise the user to clear cached credentials in Credential Manager.

## Escalation
Repeated lockouts within minutes may indicate a stuck mapped drive or a credential-stuffing attempt. If suspicious, escalate to SecOps-CSIRT.
