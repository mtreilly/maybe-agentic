---
name: find-state-machines
description: Recover implicit state machines from existing code, including scattered flags, async work, retries, cancellation, and persistence. Use for requests to find state machines or analyse lifecycle and event-order risks. Produces a read-only, evidence-linked model rather than implementing a redesign.
---

# Find the implicit state machines

Recover how the implementation moves between meaningful states. Find where correctness depends on event order, duplicated facts, or conventions that the code does not enforce. Do not assume every group of flags needs a state machine library or an enum.

This is discovery, not permission to refactor. Keep application code, tests, and configuration unchanged. Use controlled reproductions only when useful, with external effects isolated.

## Set the boundary

Follow the user's scope. For a whole-app request, inventory entry points and workflows, then inspect machines with consequential effects or complex lifecycles first. Cover the inventory and report gaps. Do not claim an exhaustive semantic analysis from a filename search.

Define what counts as observable behaviour: screens, API responses, persisted data, external writes, messages, and relevant timing or ordering guarantees. Include internal values that affect future behaviour, such as pending requests, generations, timers, queues, and transaction state. Seek the smallest useful model for that boundary, not a claim of mathematical minimality.

## Recover machines from evidence

Trace writes and event handlers through their callers and consumers. Look beyond named status fields: related booleans, nullable results, closures, subscriptions, database rows, URL state, and cleanup handlers can jointly encode a lifecycle.

For each meaningful machine, record:

- Its purpose, state owners, and implementation locations.
- Initial, intermediate, and terminal states, and how the code represents them.
- Events and transitions: source state, guard, state update, destination, and effects.
- Effect prerequisites and who enforces them. Distinguish starting an operation from accepting its eventual result.
- Interactions with other machines, including shared resources and cross-process ownership.

Use a transition table or small Mermaid diagram when it clarifies the model. Keep independent dimensions separate unless their interaction creates a relevant constraint. Do not flatten several machines into every possible combination of their states.

Separate **implemented behaviour**, **intended rules supported by requirements or tests**, and **inferred intent or unknowns**. Mark whether a state is reachable, structurally excluded, or merely conceivable. Do not draw the desired design and present it as the existing implementation.

## Challenge the transitions

Investigate risks suggested by the machine, rather than applying every check mechanically:

- **Order and repetition:** which operations commute, which are idempotent, and under what preconditions? Compare observable effects as well as final values. Include completion order, duplicate events, retries, and reentrancy where relevant.
- **Ownership and validity:** can stale completions commit after replacement, cancellation, logout, or disposal? Does a guard remain valid across an await, or need to be checked again at commit time?
- **Invariants:** which combinations must never occur, and what actually prevents them? Distinguish type, runtime, and transaction enforcement from caller convention or a test assertion.
- **Progress:** can a pending state wait forever? Account for failure, timeout, cleanup, recovery, and valid terminal states. State environmental assumptions needed for progress.
- **Duplicated facts:** can copies drift? A cache or optimistic value may be intentional. Identify authority, synchronisation, and reconciliation before recommending removal.
- **Effects without a consumer:** trace apparently wasted work through persistence, external systems, and future reads. No screen update alone does not make work unnecessary.

Nondeterminism is not itself a defect. Identify an allowed schedule that violates a supported rule. Retries and special cases may encode real requirements.

## Report findings and limits

Give a concise machine inventory, then rank concrete findings by impact and strength of evidence. For each finding, include the violated rule, code locations, existing enforcement, and the smallest reproducing trace found. A trace may need initial state, inputs, event order, failures, or environmental conditions.

For example: query A starts, query B starts, B completes, A completes, and A replaces B's results. Check whether the implementation accepts A's stale completion before reporting this as a defect. A cancellation call alone does not establish that the result cannot commit.

Label findings as reproduced, supported by a code path, or unresolved. State what was inspected, what remains unexamined, and which assumptions need confirmation. Finding no counterexample does not prove a machine correct.

Recommend explicit state or transition ownership only where it prevents a demonstrated problem or removes concrete caller obligations. A sound existing representation is a valid outcome. Discovery is complete when the scoped inventory and findings are accounted for, including declared gaps.

When implementation is requested, these findings can guide a bounded refactor with `untangle-codebase` if available. If the user explicitly requests `statechart`, pass it the relevant machine, rules, and environmental assumptions for bounded model checking. Neither skill is required for discovery.
