---
name: how
description: Explain how a subsystem works by tracing actual entry points, runtime flow, data ownership, and module boundaries. Use for code walkthroughs, onboarding explanations, and questions about where behavior or responsibility belongs.
---

# Explain how it works

Build a useful mental model from real code. Explain behavior and ownership; historical motivation needs separate evidence and must not be inferred from a function name alone.

## Ground the explanation

Identify the user's target and scope. State a reasonable interpretation when ambiguous and proceed with available evidence. For a narrow function or module, inspect directly. For a broad subsystem, divide the question into distinct angles; use independent readers only if delegation is available, authorized, and useful. No specific agent tool, model, or panel is required.

Trace a representative input from its actual entry point through important transformations, state owners, integration boundaries, and observable output. Include error or teardown paths when they change the explanation. Identify invariants, lifetimes, scheduling, and public versus internal APIs. Inspect callers and pinned dependency implementations where needed rather than explaining file names in isolation.

Read [references/explanation-guide.md](references/explanation-guide.md) when structuring a broad explanation or answering ownership/layering questions. It contains the exploration questions and presentation guide.

## Deliver a mental model

Lead with what the subsystem does and the central mechanism. Explain its key concepts, a concrete runtime flow, where responsibilities live, and the gotchas relevant to the question. Link source locations supporting important claims. Omit sections that add nothing.

Name what is directly observed, what is inferred, and what remains unknown. A source-only walkthrough does not prove the runtime was exercised. Keep a read-only question read-only; do not redesign the subsystem to explain it.

## Attribution

Adapted from Lauren Tan's pstack `how`, cursor/plugins commit `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`. Exploration and synthesis work directly without Cursor delegation. See [LICENSE.txt](LICENSE.txt).
