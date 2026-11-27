# Feature map format

The generated map is the maintained recipe for proving user-visible behavior, not a description of implementation internals.

## Index

`features/README.md` names the application, shared launch prerequisites, fixture setup, isolation rules, readiness check, artifact directory, and cleanup. Link each feature file and state its coverage. When several entry points lead to the same behavior, list them; proving one does not prove the others.

## Feature files

Each file has an H1 feature name and a sentence explaining what the user achieves. Then use:

- **Sub-features:** named behaviors and stable IDs for artifact association.
- **How to get to it:** real menus, keyboard shortcuts, routes, or commands.
- **Driving it:** prerequisites followed by action, concrete tool invocation, expected result, and evidence to capture for each relevant path.
- **Gotchas:** focus, asynchronous readiness, trimming/normalization, permissions, fixture requirements, and other observed constraints.

For a save feature, observe the saved value through a second view or a reload. For a search feature, check a matching query, a miss, clearing the query, and any distinct supported entry points. Choose cases the actual application supports.

An unreachable feature records the attempted path and missing prerequisite. Never rename an unreachable or skipped path as verified. Keep artifact references after teardown. Generated feature entries must contain real commands and values; this format is guidance, not text to paste with placeholders intact.
