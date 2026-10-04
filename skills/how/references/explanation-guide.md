# Explanation guide

For a broad subsystem, collect these facts before drafting:

- The public input or action and the actual entry point.
- The main data shape, its owner, and how its lifetime ends.
- The sequence of calls or events, including asynchronous boundaries.
- The module that owns each policy or invariant.
- External calls, persistence, cache behavior, and observable output.
- Error, cancellation, retry, and teardown behavior relevant to the question.
- The source locations establishing each non-obvious claim.

For placement questions, compare responsibilities rather than directory names. Ask which module knows the policy, which caller should be shielded from it, and whether placing it elsewhere creates duplicate state or leaks internal representation.

Present an overview, key concepts, concrete runtime flow, responsibilities, and relevant traps. A small diagram or example can replace a long call-by-call recital. Keep consumer-visible behavior ahead of implementation detail. Do not turn the answer into an annotated source dump.

Before delivering, check that a reader could predict where to change one relevant behavior and what else that change would affect. If the explanation cannot support that prediction, identify the missing ownership or flow evidence.
