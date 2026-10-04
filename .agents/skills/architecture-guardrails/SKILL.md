---
name: architecture-guardrails
description: Make established project architecture rules enforceable through types, import boundaries, contract checks, or small static checks. Use when architectural drift needs prevention or a repository convention needs an executable guard.
---

# Enforce architecture contracts

Start with a supported rule and concrete callers, not a universal ideal architecture. Repository documentation, incident evidence, public contracts, and explicit user requirements establish intent.

## Define the invariant

State the rule, its owner, source roots, legitimate exceptions, and the failure it prevents. Trace actual imports, entrypoints, generated outputs, and consumers. Separate a design preference from a correctness or ownership requirement. If intent is ambiguous, report the decision needed before enforcing it.

Examples include domain modules exposing supported interfaces, UI code using generated API clients, producer subjects having schemas, and generated files matching their canonical inputs. Rules such as file-size caps or mandatory abstraction layers need separate evidence of value.

## Choose enforcement

Prefer removing duplicate state, deriving inventories from canonical manifests, narrowing exports, and encoding invalid combinations in types. Then consider an existing compiler/linter rule, dependency graph check, schema validator, or generator consistency check. Add a custom scanner only for the remaining invariant.

Use AST or symbol analysis when aliases, nested syntax, imports, or call ownership matter. Regex is suitable for narrow textual conventions; name its blind spots and avoid reporting complete semantic coverage. Ensure newly added workspace members are included automatically.

Keep diagnostics actionable: rule, source location, why it violates the contract, and the supported alternative. Exceptions must identify the specific boundary and rationale rather than exempt a common filename everywhere. For existing debt, distinguish grandfathered violations from newly introduced ones.

## Implement and prove

Within the authorized scope, put enforcement in a portable executable command called by the project's existing gates. Keep agent integrations thin. Checking should not silently rewrite canonical or generated inputs; regeneration belongs to an explicit command.

Prove the guard rejects a realistic violation and accepts a valid use, including a legitimate exception if one exists. Test at the executable boundary without exposing production internals solely for testing. Verify file coverage, nonzero failure propagation, and missing-input behavior. Run relevant existing checks after edits.

Report the invariant, selected mechanism, proof, migration/baseline decisions, and semantic limitations. Behavioral risks that cannot be established statically need a separate verification path.
