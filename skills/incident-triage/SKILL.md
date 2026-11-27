---
name: incident-triage
description: Triage live or staging production incidents, error spikes, latency regressions, or failed deploys using logs, traces, metrics, and error trackers such as Sentry or Cloudflare Observability. Use for active operational investigation and mitigation; for local reproducible code bugs, use systematic-debugging.
---

# Live incident and observability triage

Stabilize user impact first, separate verified telemetry from theories, and isolate what changed before proposing a permanent code fix.

## Bound the blast radius

Establish the concrete scope before digging into source code:

- **What is failing:** Exact endpoints, jobs, screens, or error classes, with representative error messages and status codes.
- **Who and where:** Affected environments, regions, releases, tenants, or user cohorts versus unaffected baselines.
- **When it started:** Earliest anomaly timestamp compared against recent deploys, config/flag flips, schema migrations, certificate/secret rotations, and upstream provider status.

## Stabilize before deep root-causing

If production users are actively impacted, evaluate the fastest reversible mitigation first (feature-flag disable, release rollback, traffic shift, rate limit, or worker pause) and clearly state the tradeoff. Never mutate production state, run rollbacks, flip flags, or post external incident updates unless explicitly authorized by the user.

## Correlate telemetry systematically

Query only the observability sources relevant to the symptom (error trackers, edge/worker logs, distributed traces, database query insights, recent commits/deploys):

- Group errors by release version, stack frame, route, and upstream dependency rather than reading one event in isolation.
- Compare failing traces against a healthy baseline trace from the same path. Check latency breakdowns, retries, timeouts, queue depth, connection pools, and status codes at every boundary.
- Treat missing telemetry or unavailable connectors as explicit visibility gaps, not proof that a layer is healthy.
- Never copy raw credentials, auth headers, tokens, or sensitive customer payloads into summaries, tickets, or committed files; cite redacted IDs, trace IDs, and timestamps instead.

## Separate mitigation from permanent repair

Once the failing boundary is isolated in telemetry and mapped to source:

- Label every claim as **observed in telemetry**, **supported by source**, or **unverified hypothesis**.
- Distinguish immediate **mitigation** (stops the bleeding) from **root-cause repair** (prevents recurrence) and **observability gaps** (blind spots that slowed detection or isolation).
- Hand off confirmed local code defects to normal scoped debugging and regression testing rather than hot-patching blindly during triage.

## Report

Lead with current status, user impact, and recommended immediate action (if any). Follow with a concise UTC timeline, correlated telemetry evidence (trace/event IDs, deploy SHAs, queries run), narrowed cause or ranked hypotheses, visibility gaps, and prioritized follow-up actions.
