# Runbook RB-002: VPN Connection Failures

Category: network
Symptoms: Cannot connect to corporate VPN, authentication timeouts, or frequent drops.

## Resolution Steps
1. Confirm internet connectivity outside the VPN (open a public site).
2. Verify the VPN client is current; update if an older build.
3. Flush DNS: `ipconfig /flushdns`. Reset Winsock: `netsh winsock reset` then reboot.
4. Confirm MFA token/time sync on the authenticator app.
5. Try an alternate VPN gateway/region if available.

## Escalation
Persistent failures across multiple users indicate a gateway outage. Escalate to Network-Operations as P2.
