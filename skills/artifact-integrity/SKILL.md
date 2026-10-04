---
name: artifact-integrity
description: Recommend or implement deterministic integrity checks for documentation, schemas, configuration, localization, datasets, or agent setup artifacts. Use when related non-code files drift or their structural contracts need executable validation.
---

# Validate maintained artifacts

Treat maintained artifacts as interfaces with owners and sources of truth. Validate relationships that matter to their consumers rather than imposing generic formatting policies.

## Identify contracts

Inspect the requested artifact family, its consumers, generator/manifests, and existing validators. Define what is canonical, derived, historical evidence, or scratch. Historical evidence is not rewritten to satisfy current expectations. Missing expected inputs must be reported rather than yielding an empty successful scan.

Select relevant checks:

- Documentation: local link targets and anchors, canonical index entries, referenced commands/paths, and required evidence links. Distinguish structural validity from factual accuracy; do not network-check every URL by default.
- Schemas and configuration: parse/schema validity, referenced files, example validation, producer/consumer coverage, and generated-output drift.
- Localization: key and namespace coverage, interpolation placeholder parity, intentional fallback policy, and manifest/resource consistency. Dynamic keys require explicit ownership; unused-key detection alone is not proof of dead content.
- Datasets: declared column types, nullability, uniqueness, referential integrity, and domain ranges. Use an explicit sample or full scope and report which was checked; do not silently repair data or expose sensitive rows.
- Agent setups: frontmatter names, manifest/source parity, supporting links, client symlinks, installed-copy freshness, provenance/licenses, and setup reproducibility. Frontmatter validation does not establish skill behavior.

## Build a proportionate validator

Use a native parser or existing validator before writing regex. Derive related inventories from one canonical manifest where possible. Separate deterministic local validation from checks needing live systems. Keep domain rules explicit and avoid universal thresholds without an owner.

Use stable file ordering, useful paths/locations in diagnostics, nonzero failure codes, and precise exceptions. Read-only validation should not regenerate, rewrite, install, or contact services as a hidden side effect. Provide a separate explicit repair command if needed.

## Verify and deliver

Recommendations produce a risk-to-check plan with exact commands and costs. Implementation requests authorize relevant validators and integration in existing project gates. Demonstrate a valid artifact passes and a realistic broken relationship fails; verify missing-input and newly added artifact coverage where relevant.

Report checked scope, changes, failures, exclusions, and limitations. Schema validity cannot prove a claim is true or an artifact is operationally correct; identify where human review or behavioral verification remains necessary.
