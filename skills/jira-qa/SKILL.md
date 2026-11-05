---
name: jira-qa
description: Define ticket QA criteria, run visual Playwright checks, and prepare formatted Jira results with screenshots, recordings, and supporting comments. Use for ticket QA plans, verification, retests, and QA reports. Posting results requires existing user authorisation.
---

# Jira QA

Produce a reproducible QA record with acceptance criteria, an environment box, scenario results, and evidence.
Use Órlaith's [INT-9297 comment](https://vsware.atlassian.net/browse/INT-9297?focusedCommentId=74506) as the format reference.
The reference records the environment, a green QA PASS verdict, an observed result, and before/after evidence.
This skill adds explicit criteria, failure details, and blocked results.

## Scope and authorisation

- A request for criteria produces a test plan with PENDING results. It does not claim completed checks.
- A request to run QA includes browser checks and a complete report within the authorised environment.
- Post comments or upload evidence when the user authorises Jira reporting. Otherwise deliver a complete draft with local evidence links.
- Reuse existing authorisation. Do not add a confirmation step when the user already requested publication.
- QA does not authorise deployment, production changes, sending mail, or unrelated source fixes.
- Follow project instructions for credentials, test data, browser tools, and permitted mutations. Never include credentials or session tokens in evidence.

## Define acceptance criteria

Read the ticket, relevant comments, and the actual changes. Identify the behaviour the fix promises.
Read deployment information when available. A branch name does not prove which build is running.

Assign stable scenario IDs such as QA-01. For each scenario, record:

- The criterion, role, route, and relevant preconditions.
- The shortest repeatable actions.
- An observable expected result, defined before execution.
- The actual result, verdict, and evidence references after execution.

Cover the reported regression and the nearby behaviour the change could break.
Include permissions, persistence, keyboard use, and error states when the change affects them.
For responsive changes, check distinct layouts and both sides of the changed breakpoints.
In frontend-upgrade, use 320, 375, 768, 1024, and 1440px, plus relevant breakpoint boundaries.
Split broad work by feature and role. Preserve completed results so one failure does not restart unrelated checks.

## Run visual Playwright checks

UI QA requires a real browser run with Playwright. Builds, lint, source review, and DOM assertions alone cannot establish a visual pass.
Use the project's Playwright setup and required runtime. Reuse existing tests where they exercise the required behaviour.
Use separate browser contexts for different roles. Record whether the data is live, disposable, mocked, or seeded.

For each affected layout or meaningful UI state:

1. Open the route and establish the required state with real interactions.
2. Wait for observable readiness, such as loaded data or dialog focus. Avoid arbitrary sleeps.
3. Assert the expected behaviour and inspect the rendered screen through a screenshot or browser image.
4. Check visibility, clipping, overlap, scrolling, and relevant focus states. An element existing in the DOM is insufficient.
5. Exercise the affected controls. For authorised saves, check the response and persisted state after reload or refetch.

Inspect the images yourself. Saving an image without viewing it does not complete the visual check.
Keep representative screenshots when they demonstrate acceptance or explain a result.
Capture a screenshot for visible failures and visible service errors when possible.
Use video when timing, motion, an interaction sequence, or an intermittent failure needs demonstration.
Read [references/evidence.md](references/evidence.md) when capturing or preparing evidence.

Capture relevant request failures and browser errors. Identify the endpoint and status for a service blocker.
If the backend blocks a real route, isolate component checks where useful and label their scope accurately.
Do not convert isolated browser checks into a deployed QA pass.

## Decide the result

| Verdict | Meaning |
| --- | --- |
| QA PASS | Every required criterion passed in the stated environment and scope. Visual checks completed for affected UI. |
| QA FAIL | At least one observed behaviour contradicts a required criterion. |
| QA BLOCKED | A dependency or environment problem prevents a required check. |
| QA PENDING | The plan contains checks that have not started or remain incomplete without an established blocker. |

An observed acceptance failure makes the overall verdict QA FAIL, even when blockers prevent other checks.
Otherwise, a required blocker makes the overall verdict QA BLOCKED.
Use QA PENDING for remaining required work. Use QA PASS only when no required work remains.
Keep each scenario's own result visible. Exclude optional checks explicitly from the acceptance scope.

State whether the run covers local development, isolated fixtures, deployed QA, or production verification.
Local success can be a scoped QA PASS. It cannot establish deployed QA or production success.
Keep build, type, lint, and unit-test results in a separate supporting-validation paragraph.

## Report and retain evidence

Use the environment box and results table in [references/jira-report.md](references/jira-report.md).
Use a native two-column Jira table with bold field labels. Colour the verdict, while retaining its full text.
Include the tester, tenant URL, role, device/browser, viewport, tested build or commit, and relevant service versions.
Identify automated runs as Codex / Playwright. Do not attribute them to a human tester.

Every failure needs a clear problem statement, reproduction steps, expected result, actual result, and evidence references.
Each associated image, video, and supporting comment must identify that problem in its own caption or text.
Include video timestamps when the problem appears partway through a recording.
If capture fails, record the capture error and remaining evidence gap. Do not invent evidence or hide the failure.

When the user authorises publication, prefer their chosen Jira tool. Use an available connector or the Jira CLI as appropriate.
Check the installed tool's rich-text and attachment support. Do not assume Markdown pipes become a native Jira table.
Upload evidence through a supported method and use the returned attachment links or media references.
Read back the comment to check the table, verdict, captions, and accessible evidence links.
If formatting or upload is unavailable, report the limitation and provide the complete draft and retained files.

Keep one summary per run. Add supporting comments for detailed failures or later evidence, linked by scenario ID.
Identify retests with the new run and build. Preserve prior failure evidence and clearly label its superseded result.
Finish with the verdict, scope, issue/comment link or draft path, and unresolved failures or blockers.
