# Runbook RB-001: Outlook Crashes on Launch

Category: email_collaboration
Symptoms: Outlook closes immediately on startup, often after a Windows or Office update.

## Resolution Steps
1. Start Outlook in safe mode: press Win+R, type `outlook /safe`, press Enter.
2. If it opens in safe mode, disable add-ins: File > Options > Add-ins > COM Add-ins > Go, uncheck all, restart.
3. Repair the Office installation: Settings > Apps > Microsoft 365 > Modify > Quick Repair.
4. If still failing, rebuild the Outlook profile: Control Panel > Mail > Show Profiles > Add a new profile.
5. Re-enable add-ins one at a time to identify the culprit.

## Escalation
If crash persists after profile rebuild, escalate to Messaging-Team with the crash event ID from Event Viewer.
