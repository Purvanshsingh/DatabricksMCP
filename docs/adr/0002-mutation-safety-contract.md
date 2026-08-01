# ADR 0002: Mutation safety contract before write tools

- Status: Accepted
- Date: 2026-08-02

## Context

Read-only coverage now spans the major Databricks domains. Adding
state-changing tools is the next step, but language-model tool selection is
probabilistic and prompt content is untrusted, so an accidental or injected
call to a destructive tool must not be able to change or destroy state.

## Decision

No write tool executes except through a single contract
(`MutationController.run`):

1. **Policy** — writes are denied unless `access_mode=controlled-write` *and*
   the specific tool is on `write_tools_allow`. Read tools are unaffected.
2. **Dry-run** — callers can request a plan (risk, target, argument fingerprint)
   without executing; for high-risk actions the plan includes an approval token.
3. **Approval** — destructive and privileged actions require a short-lived,
   single-use token bound to the exact tool and arguments. Wrong-argument,
   wrong-tool, expired, and replayed tokens are rejected.
4. **Audit** — every branch (denied, dry-run, approval-required, executed,
   error) emits a structured event containing no argument values.

Write packs are registered only in controlled-write mode, so they are invisible
by default.

## Consequences

The default deployment cannot change state at all. Enabling writes is explicit,
per-tool, and — for destructive actions — per-invocation. The contract is the
single place to extend for idempotency stores, quotas, and richer approval
workflows, keeping every future write pack uniform.
