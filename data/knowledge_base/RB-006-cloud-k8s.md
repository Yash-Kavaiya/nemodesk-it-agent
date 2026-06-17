# Runbook RB-006: Kubernetes Pod / Cloud Workload Issues

Category: cloud_infra
Symptoms: Pods crash-looping, ImagePullBackOff, service unreachable, high latency.

## Resolution Steps
1. `kubectl get pods -n <ns>` to see status; `kubectl describe pod <pod>` for events.
2. CrashLoopBackOff: check `kubectl logs <pod> --previous` for the failure reason.
3. ImagePullBackOff: verify image tag and registry credentials (imagePullSecrets).
4. Resource pressure: check requests/limits and node capacity (`kubectl top`).
5. Networking: verify Service selectors and NetworkPolicy.

## Escalation
Cluster-wide impact or control-plane errors -> escalate to Cloud-Platform as P2/P1 depending on blast radius.
