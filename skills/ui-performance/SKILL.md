---
name: ui-performance
description: Diagnose and improve frontend rendering performance when animations stutter, scrolling slows, React renders every frame, or motion causes visual shifts. Use for UI performance reviews and fixes rather than visual design critique or general backend performance.
---

# UI performance

Find the rendering work behind a slow interaction and make the smallest change that addresses it. This skill adapts Emil Kowalski's [Performance Cheatsheet](https://github.com/emilkowalski/skills/blob/main/performance-cheatsheet.md) into a diagnosis and verification workflow.

## Establish the cause

Identify the affected component, interaction, animation library, and device or viewport where the problem appears. Reproduce the actual interaction with realistic data. When profiling tools are available, record a baseline and distinguish layout, paint, compositing, JavaScript, and React render work. Use the project's existing browser and profiler tools; no particular integration is required.

If profiling is unavailable, inspect the implementation and label proposed causes as hypotheses. Do not claim a frame-rate improvement from a code change alone. Follow the user's requested scope: a review produces findings; a request to fix performance includes implementing and verifying the relevant changes.

## Choose a targeted fix

| Symptom | What to investigate | Candidate fix |
| --- | --- | --- |
| Animation stutters | Per-frame changes to dimensions or position trigger layout/paint. | Prefer `transform` and `opacity` when they preserve the intended behavior. Transforming an element does not reflow its siblings; retain necessary layout animation and measure it. |
| Long lists scroll slowly | Too many mounted rows, expensive row rendering, or slow event handlers. | Virtualize when offscreen rows dominate the work. Preserve stable keys, focus, keyboard navigation, variable row heights, and scroll position; consider pagination if it better fits the product. |
| Animated blur is expensive | Large filtered areas, filter radius, overlapping layers, and device constraints. | Reduce blur radius, affected area, or overlap; consider a static blur with an opacity transition. Emil's under-20px advice is a starting heuristic, not a universal performance guarantee. |
| Motion `x`/`y` animation drops frames | How the installed Motion version constructs transforms and whether the workload runs on the main thread. | Trial animating the full `transform` string if it preserves composition with existing transforms. Compare traces before replacing the API; this is not inherently faster in every version or browser. |
| Unrelated properties animate | `transition: all` catches properties changed elsewhere, including layout properties. | List the intended transition properties explicitly, preserving the required interaction. |
| React renders every animation frame | Frame-loop state updates cause component work even when only a visual value changes. | Move purely visual frame updates to CSS, the animation library's motion values, or a ref-owned style. Keep semantic application state in React; avoid competing React and imperative ownership of the same style. |
| Element shifts by a pixel as motion starts | Transform rounding, changed layout, or layer promotion at animation start. | After reproducing and checking the cause, trial `will-change: transform` before the animation. Use it narrowly and remove it when no longer needed; extra layers consume memory and can change rendering. |

Avoid applying every optimization in the table. Fix the measured or well-supported bottleneck. Do not add virtualization, imperative style writes, or persistent `will-change` merely because the code uses a list, React, or animation.

## Verify the result

- Repeat the same interaction with the same data, viewport, device constraints, and build mode. Compare production-like builds where practical; React development overhead can distort results.
- Compare the evidence relevant to the cause: frame timings, dropped frames, layout/paint work, main-thread duration, mounted row count, or React commits. Report observations without inventing measurements or hard thresholds.
- Check that the change preserves layout, transforms, scroll behavior, focus, and keyboard operation. Retain reduced-motion behavior; do not trade accessibility for smoother animation.
- Run relevant existing checks for the touched code. A narrow style change may need a browser check; changes to list behavior or state ownership need verification of the affected interactions.

## Report

For each finding, state the affected file and interaction, evidence or hypothesis, proposed or applied fix, and its tradeoff. For implemented changes, include before/after observations and any verification limits. If the bottleneck lies outside this skill's scope, name that evidence and recommend the next investigation instead of forcing a rendering fix.

## Attribution

Adapted from Emil Kowalski's `performance-cheatsheet.md` at upstream commit `e8a175de22ae` in the research inbox. Workflow, qualifications, and verification guidance are maintained locally. The upstream MIT license is included in [LICENSE.txt](LICENSE.txt).
