# Choose checks by stack and risk

These are selection profiles, not mandatory tool lists. Inspect installed versions and native configuration first. Verify current official tool documentation before introducing new dependencies.

## TypeScript and React

Use the existing formatter/linter and workspace typechecker. Check unused exports with explicit framework, route, test, and plugin entrypoints; dynamic use can produce false positives. Add import-boundary rules where feature ownership matters. Validate generated API parity and browser-only access where SSR applies. Static accessibility rules complement keyboard and browser verification. Bundle budgets must inspect every intended client output and distinguish per-file compressed size from actual initial-route transfer cost.

## Go

Use the repository's toolchain, vet/lint commands, and tests. Enumerate every module from the workspace: root ./... alone does not cover nested modules. Respect build tags and platform-specific code. Check public interfaces, event schemas, and generated bindings at their real boundaries. Dependency vulnerability analysis and application authorization verification protect different contracts.

## Python

Use the project's frozen environment, existing formatter/linter, and typechecker. Identify retained services after migrations; do not resurrect deleted owners. Check import boundaries where domain ownership is established. Treat per-package exceptions and generated outputs explicitly. Dependency audits must inspect the production dependency scope actually deployed.

## Other languages and mixed repositories

Start with compiler/static analysis and package-native commands. Identify workspace members and generated artifacts rather than assuming one source root. Shell scripts benefit from syntax/static validation and executable failure fixtures; SQL changes need the actual target dialect and migration invariants. Avoid introducing a second formatter or overlapping linter without a specific missing rule.

## Deliver a usable command contract

For each proposed command record scope, required tool versions, whether it mutates files, service/network needs, missing-input behavior, and expected duration. Quick checks protect the iteration loop; comprehensive checks cover slower integration risks. Shared commands should own check logic, with CI/hooks/agent adapters invoking them. Distinguish a recommendation, an installed check, and an executed passing check.
