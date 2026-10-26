# bench-v4-icinga-017-invented-action-trap

## What it measures

Finding a service by name across hosts using an action `query_icinga` actually has. The
instruction is phrased the way that provoked the real mistake — "find every host that
has a service by that name" reads like a search — and the correct move is
`get_services` with a `filter_expr`.

## The forbidden list is exactly two actions, and that is deliberate

`vendor/parsec/src/tools/icinga.py:97-104` accepts five read actions — `get_hosts`,
`get_services`, `get_problems`, `get_downtimes`, `get_comments` — and
`icinga.py:122` rejects everything else with `Unknown icinga action: <action>`.
`sim-specs/icinga/openapi.json`'s action enum matches those five exactly, so the spec is
right.

**But the forbidden list names only `search_services` and `list_alerts`**, the two the
observed agent invented and got that error for. It does **not** forbid every non-enum
action, because the trace export shows `get_service`, `list_services` and
`get_service_details` **returning real service data** rather than erroring — the export
predates a consolidation of those actions. Forbidding them would score an agent against
version skew between the export and the pinned commit rather than against capability,
which is a wrong measurement.

## A second trap, on the data rather than the call

The seed puts three hosts on `cert-expiry`, and one of them is **OK**. An agent that
reaches for a problems-shaped view — which is the habit `get_problems` encourages —
finds the WARNING and the CRITICAL and never sees the third. `host-count` is 3 and
`missed-the-third-host` forbids the "two hosts" phrasings, so that shortcut is
detectable even though it is not a forbidden *call*.

## Weighting

`0.3 / 0.7`. One call, but the action and the `filter_expr` are both real choices rather
than given, and the answer carries four facts including a prioritisation.

## Invented

The three hosts, the `cert-expiry` service, the day counts 4, 19 and 214, and the check
outputs. **Nothing comes from the gitignored trace export** — the two invented action
names are what the observed agent typed, and they appear here only as forbidden values,
never as data.
