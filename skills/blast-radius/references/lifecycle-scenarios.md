# Lifecycle and recovery scenarios

Use this reference when the changed contract spans time, authority, asynchronous
work, derived data, or resource ownership. Pick the smallest useful set based on
actual callers and failure mechanisms. These are investigation lenses, not
mandatory tests or universal implementation rules.

## Alternate callers and final responses

Trace commands, queries, timers, reactions, HTTP routes, generated clients, share
links, and browser/mobile transports that actually reach the changed behavior.
A guard in one handler may leave another path open. Follow restricted data into
metadata, explanations, errors, exports, and the final response; a safe message
body alone does not establish a safe externally shared artifact.

Example: access denied by the normal UI may still succeed through a share link
or a background reaction. Verify as the actor who could bypass the first guard.

## Authority changes at the point of use

Where the contract requires current authority, examine revocation, session
replacement, changed scope, and permission loss between preview and execution or
while a request is held. Determine how authorization and the action stay
consistent; do not prescribe a transaction when the architecture uses another
valid mechanism. Equal aggregate totals do not prove equal authorized subjects.

Example: a queued operation accepted before a grant is revoked must follow the
project's stated execution policy when it eventually runs. Retained cache/storage
must obey the corresponding visibility and deletion policy too.

## Effective time and later events

Inspect the requested instant and the owning organization's time zone. Distinguish
recording a future-valid fact from the moment it becomes valid. Exercise early
ends, extensions, future amendments, and dependent timers or grants where relevant.
Preserve unaffected later segments according to the domain contract.

Example: recording a renewal today may not authorize an action until its validity
starts. A clock-change scenario should cover service dates on both sides of the
transition, rather than assuming the first two scheduled events use different
offsets. Never use the developer machine's date as an implicit domain clock.

## Retries, concurrency, and uncertain outcomes

Follow duplicate delivery, reordered events, competing requests, and lost responses
after a successful side effect. Establish who owns idempotency, ordering, and retry
state and whether restart preserves the promised guarantees.

Example: editing a form after preview must not silently change an already captured
confirmation payload. Retrying an uncertain execution should retain the payload
and idempotency identity required by the contract. In-memory state alone cannot
establish durable replay.

## Projections and rebuilds

Compare incremental updates with recovery after missed delivery or a fresh rebuild.
Include records that should disappear after cancellation, withdrawal, correction,
or scope changes. Compare every field that establishes the contract, not merely
row count. Inspect derived indexes, caches, and public copies as well as the owner.

Example: a rebuild that adds current records but retains obsolete ones can pass a
happy-path search test while exposing withdrawn material. Reconciliation needs a
case with both retained and removed records.

## Teardown and durable cleanup

Trace overlapping sessions, replaced owners, cancellation, unmount, and process
restart. Check resource identity, abort propagation, and whether cleanup completion
must precede a replacement. An in-memory cache test does not establish deletion
from browser or database storage: reopen the persisted store where that is the
observable contract. Remove only resources owned by the verification run.

## Turn a concern into evidence

For each selected scenario record: the invariant, concrete actor and initial state,
trigger or later event, reachable entry point, expected visible outcome, and the
cheapest executable proof. Use existing tests or real workflows first. A new test
should protect a distinct contract, not repeat an internal implementation.

Mark source reasoning, executed proof, and unresolved prerequisites separately.
Do not claim a class is safe because one unrelated scenario passed. Report product
regressions separately from test-environment failures.
