# Runbook RB-004: Laptop Hardware Issues

Category: hardware
Symptoms: Won't power on, battery not charging, external monitor not detected, dock issues.

## Resolution Steps
1. Power: hold power button 30s (hard reset), connect known-good charger, check charging LED.
2. Display: reseat the dock/cable, try a different port, update graphics driver, Win+P to switch display mode.
3. Battery: check battery health report (`powercfg /batteryreport`).
4. Peripherals: test on another machine to isolate device vs. laptop.

## Escalation
Confirmed hardware fault (no power, swollen battery, dead port) -> dispatch Field-Support for repair/replacement; provide asset tag.
