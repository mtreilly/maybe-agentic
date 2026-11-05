# Visual evidence

Evidence must show the tested behaviour and explain its relevance without requiring the reader to guess.

## Playwright capture

Use the project's browser setup and authentication. Wait for the relevant state before capture.
Record the role, route, viewport, build, run, and scenario alongside each artifact.

For screenshots:

- Capture the relevant screen or component with enough surrounding context to identify it.
- For overlap or clipping, show the actual viewport. A full-page image alone can hide the problem.
- For missing controls, show the open menu or expected location and identify the missing item in the caption.
- For focus problems, capture the focus state and describe the keyboard sequence that produced it.
- Preserve the original capture if you add arrows, outlines, or other annotations to a copy.
- Inspect the saved image. Check it shows the stated outcome at a useful size.

Keep screenshots for material visual acceptance checks and visible failures.
One image can support several related assertions when its caption explains them clearly.
Do not collect redundant screenshots of every click.
For a nonvisual check, request/response evidence or test output can be sufficient. Explain why an image adds no value.

## Videos

Record when a screenshot cannot explain the sequence, timing, motion, focus movement, or intermittent behaviour.
Start recording before the reproduction steps. Stop after the outcome is clear.
Keep a short recording of the relevant flow instead of an unexplained full-session recording.
Finalise the Playwright context before linking a recording so the video file is complete.
Watch the relevant section before describing it. Include timestamps for the action and the failure.

If a failure appears without video, preserve its screenshot and logs first.
Rerun the same scenario with recording when useful and safe. Do not discard the original failure if reproduction is intermittent.
Record the observed failure count and attempt count when they affect confidence.
Playwright traces can support diagnosis. Explain which event matters, and retain visual evidence for visible UI problems.

## Names and captions

Use filenames that identify the verdict, scenario, and symptom or successful behaviour.

```text
int-1234-run-01-qa-02-fail-whats-new-missing-375x812.png
int-1234-run-01-qa-02-fail-whats-new-missing-375x812.webm
int-1234-run-02-qa-02-pass-more-shows-whats-new-375x812.png
```

Give every failure image or video its own caption:

```text
FAIL · QA-02 · What's New is absent from More at 375×812.
Principal account, QA build [recorded version], run 01.
Expected: More displays What's New.
Actual: the open menu has no What's New entry.
Video: 00:06 opens More. 00:08–00:10 shows the missing entry.
```

Replace the example version with the recorded value. Use Not recorded when unavailable.
Captions, attachment names, and supporting comments must describe the same observed problem.
Avoid names such as `screenshot.png`, titles such as `broken`, and captions such as `see attached`.
Label before/after evidence and identify its build. An after-fix screenshot can still demonstrate QA FAIL.

## Storage and attachments

Use a stable run directory or the project's test artifact directory. Do not rely on temporary files as the only retained evidence.
Report local artifact paths when results remain a draft. Check that files exist. Finalise recordings before linking them.
For published Jira reports, upload the artifacts or use durable links accessible to the intended QA readers.
Local filesystem links cannot serve as shared Jira attachments.
Check uploads and links before marking evidence complete.
If an upload fails, retain the files and explain the gap in the report.

Avoid capturing unrelated personal data. Use disposable records where possible.
Remove credentials and session tokens from logs, images, recordings, and traces before sharing them.
