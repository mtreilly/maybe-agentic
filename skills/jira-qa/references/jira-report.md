# Jira report format

Use this structure for a plan or completed run. Replace example values with observed facts.
The tables below describe the layout. Published Jira comments must use actual rich-text table cells.

## Environment box

| Field | Value |
| --- | --- |
| **Result** | QA PASS / QA FAIL / QA BLOCKED / QA PENDING |
| **Tested by** | Tester name, or Codex / Playwright |
| **Run** | Ticket key, run identifier, date, time, and timezone |
| **Tenant** | Tested school/environment URL |
| **Login** | Role and relevant permissions, without credentials |
| **Device** | Operating system, browser name, and browser version |
| **Viewport** | Tested width × height values in CSS pixels |
| **FE** | Deployed frontend version and verified commit when available |
| **Services** | Relevant service names and tested versions |
| **Scope / data** | Local, isolated, deployed QA, or production. State whether the run uses mocked or real data. |

Use `Not recorded` for unknown build details. Use `Not applicable` only when a field genuinely does not apply.
Combine FE and services in one row with line breaks if that improves readability.
Use green for QA PASS, red for QA FAIL, amber for QA BLOCKED, and neutral grey for QA PENDING.
Colour supports the written verdict. It never replaces the verdict text.

Órlaith's original QA PASS uses green `#36b37e`. Keep equivalent colours if the Jira editor offers a different palette.

## Result and scenarios

Start the body with `RESULT: QA PASS`, `RESULT: QA FAIL`, `RESULT: QA BLOCKED`, or `RESULT: QA PENDING`.
Follow it with one sentence describing the observed outcome or the work still required.

| ID | Criterion and actions | Expected | Actual | Result | Evidence |
| --- | --- | --- | --- | --- | --- |
| QA-01 | Role, route, preconditions, and repeatable actions | Observable behaviour | Observation, or Not run | PASS / FAIL / BLOCKED / PENDING | Evidence IDs and links |

Use multiple rows for materially different roles, layouts, or outcomes.
Do not compress passed desktop checks and a failed mobile check into one PASS row.

## Evidence blocks

For a pass, state what the image or recording proves:

> **PASS · QA-01 · After fix · 375×812 · Principal**
> More displays Academic Year and What's New. Both controls remain fully visible.
> Evidence E-01: screenshot link.

Include before-fix evidence when available and useful. Do not fabricate it or change a shared environment to obtain it.

For a failure, make the problem understandable beside each attachment:

> **FAIL · QA-02 · What's New missing from More · 375×812 · Principal**
> Steps: open the dashboard, then select More.
> Expected: More contains What's New.
> Actual: More opens, but What's New is absent.
> Impact: the principal cannot open release notes at this width.
> Evidence E-02: screenshot link. The open More menu lacks the expected entry.
> Evidence E-03: video link, 00:06–00:10. More opens and the entry remains absent.

For a blocker, distinguish missing coverage from an observed product defect:

> **BLOCKED · QA-03 · Login unavailable on QA**
> The tenant request returns HTTP 503 before the staff navigation loads.
> The required navigation checks remain untested on this build.
> Evidence E-04: screenshot link with the connection error visible.
> Network detail: request method, redacted endpoint, status, and time.

If a UI displays a broken state despite a successful service response, assess that behaviour as a possible QA FAIL.
An external service error can also reveal a separate failure in the UI's error handling.

## Supporting comments and retests

Keep detailed supporting comments self-contained. Start with the verdict, scenario ID, and concrete problem.
Include the run/build, role, viewport, reproduction steps, expected/actual result, and evidence links.
Link the supporting comment from the summary. Never use a bare attachment or a comment that only says "see video".

A retest records the new build and its outcome. Link the prior failure and the new evidence.
Label old screenshots and recordings as the previous run. Do not present them as evidence for the new build.

## Publication details

Use the tool's supported HTML or Atlassian Document Format for native Jira tables.
In ADF, the box uses `table` → `tableRow` → `tableCell` nodes.
Bold labels use `strong` marks. Coloured verdicts use `textColor` marks.
Images and videos use real uploaded media references or accessible attachment links.

The Jira CLI supports comment templates in the installed version:

```sh
jira issue comment add INT-1234 --template /path/to/qa-comment.txt --no-input
```

This command does not prove rich-text or attachment support. Inspect the actual result before relying on it.
If the CLI strips required formatting, use an available rich-text connector or authenticated Jira REST operation.
Keep the user's Jira tool preference where it can satisfy the required output.
For raw read-back, inspect `jira issue view INT-1234 --raw` and locate the returned comment ID.
Page comments through a supported API if the desired comment is outside the embedded result.
Check native table nodes, verdict text/colour, captions, and uploaded evidence references.
