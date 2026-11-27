---
name: db-migrations
description: Design, review, or execute zero-downtime database schema migrations, indexes, constraints, and backfills across mixed application versions. Use when changing tables, columns, keys, or data layouts in production or staging databases.
---

# Safe database migrations and rollouts

Change schemas and data without locking active traffic or breaking running application instances. Treat every production migration as a mixed-version rollout where old and new code read and write the same database simultaneously.

## Inspect the database and migration contract

Read the schema definition, migration runner, ORM/query layer, deployment order, and database engine (PostgreSQL, MySQL/PlanetScale, SQLite, or other). Confirm:

- Which table sizes, traffic patterns, and replication/online-DDL tools exist (for example, PlanetScale deploy requests, `pt-online-schema-change`, or native PostgreSQL concurrent operations).
- Whether code deploys before, after, or concurrently with migrations, and whether old application pods remain live during rollout or rollback.
- Which readers, workers, exports, webhooks, or analytics consumers touch the affected tables.

## Use expand-and-contract for breaking changes

Never rename, drop, narrow, or change the semantics of a live column or constraint in a single release when old code may still run:

1. **Expand:** Add nullable columns, new tables, or dual-write hooks while keeping the existing schema valid for old code.
2. **Backfill:** Populate existing rows in bounded, idempotent batches with progress checkpoints and explicit throttling or pause/resume behavior. Avoid single-transaction full-table updates.
3. **Verify and switch reads:** Confirm backfill completeness and parity (counts, nullability, sample/checksum checks) before switching readers to the new shape.
4. **Contract:** Drop legacy columns, fallback paths, or dual-writes only in a later release after old code can no longer be rolled back into service.

## Avoid lock and rewrite hazards

Check engine-specific locking behavior before approving DDL:

- **Indexes:** Build indexes online (`CREATE INDEX CONCURRENTLY` in PostgreSQL, online DDL in MySQL/PlanetScale) outside multi-statement transactions when supported.
- **Constraints and defaults:** Validate `NOT NULL` and `CHECK` / foreign-key constraints in two steps (`NOT VALID` then `VALIDATE CONSTRAINT` in PostgreSQL) rather than holding full-table access-exclusive locks while scanning.
- **Type changes and triggers:** Flag operations that trigger full table rewrites, cascade locks across foreign keys, or break replica lag budgets.
- **Lock and statement timeouts:** Set explicit `lock_timeout` and `statement_timeout` bounds where supported so a blocked migration aborts instead of queuing application traffic behind it.

## Define rollback, abort criteria, and verification

Before running or approving a migration, write down:

- **Abort criteria:** Lock wait time, error rate, replica lag, or row-mismatch thresholds that halt the rollout or backfill.
- **Rollback reality:** Distinguish reversible schema steps from irreversible data loss. A down-migration that drops a column with new writes is destructive, not a safe rollback.
- **Verification:** Run the migration up against a realistic local or branch database, confirm query plans for affected indexes, and test both old-code and new-code read/write compatibility where feasible. Never execute migrations against production unless explicitly authorized.

Deliver the migration plan or files, lock/compatibility analysis, backfill strategy, abort/rollback limits, and verification results.
