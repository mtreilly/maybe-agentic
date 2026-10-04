---
name: benchmark-checklist
description: Review performance measurements before reporting a speedup, regression, or comparison. Use to validate timed work, output correctness, tuning, bottlenecks, repeatability, and relevance to the user's workload.
---

# Benchmark checklist

Check the evidence behind the exact claim being made. Write the intended claim with its workload and metric before deciding what to measure. Read the measurement script to identify what it times, counts, and excludes.

## Check measurement validity

1. **Did the work happen?** Confirm requests reached the target, generators were consumed, promises were awaited, results were used, and writes or reads actually completed inside the timed region. Detect cache hits, no-ops, or early exits that invalidate the comparison.
2. **Was the output correct?** Count errors, non-success responses, retries, and timeouts. Validate result contents, not just presence. Fast rejection is not higher successful throughput.
3. **What limits the result?** Profile separately from reported timing runs. Identify CPU, allocation, I/O, locks, rendering, or another limiting resource and map it to the implementation. Check the load generator too; a saturated driver can measure itself.
4. **Was each side fairly configured?** Use comparable builds, versions, data, concurrency, cache conditions, batching, transaction behavior, and pools. For an adoption decision, compare reasonably tuned options. If deliberately comparing current deployed defaults, state that narrower claim and the configuration differences.
5. **Is the number plausible?** Compare throughput with disk/network/core limits and the time saved with the changed work's original share. Removing 10% of total time can reduce total time by at most 10%, equivalent to about 11% higher throughput for that fixed workload. A result beyond that needs an explanation such as secondary effects or invalid measurement.
6. **Does it reproduce?** Repeat and interleave baseline/candidate runs to expose warmup, cache, and machine-load effects. Use enough samples to distinguish the observed difference from noise. Report run count, a suitable central statistic, and dispersion; do not assume five runs establish significance for every workload.
7. **Does it matter to the user?** Pair microbenchmarks with the relevant end-to-end path and realistic workload. State the optimized helper's share of the total and any latency, memory, or correctness tradeoff.

Use the environment's available profiler and system tools; no particular operating system or plugin is required. If the machine is busy, either control the interference or interleave runs and disclose it.

## Scale to the decision

For an explicitly requested ballpark estimate, one run may suffice. Still check completed work and correct outputs, label the estimate, and avoid a winner claim. A choice between implementations or a claimed optimization needs stronger comparative evidence.

## Report

Give a verdict of faster, slower, no measurable difference, or inconclusive. Include the metric and unit, workload, before/after values, sample count and variation, configuration, limiting resource when known, and artifact location. Narrow or mark the conclusion inconclusive when an unchecked condition could explain the result. Keep profiling overhead out of reported timings.

## Attribution

Adapted from Lauren Tan's pstack `benchmark-checklist`, cursor/plugins commit `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`. Cross-skill calls were removed and measurement requirements made workload-dependent. See [LICENSE.txt](LICENSE.txt).
