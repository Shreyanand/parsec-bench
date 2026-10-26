# bench-v4-icinga-010-stuck-anarchysubjects

## What it measures

The shape B skeleton, which 16 real trajectories follow: locate the service, get its
detailed state, check comments and downtimes for suppression, then read the check
script from GitHub so the verdict rests on the configured threshold rather than on the
alert's own wording.

## The fact that proves the GitHub leg happened

`crit-threshold` (5) appears in **both** the check script and the alert output, so an
agent that never opened the script can still report it. `warn-threshold` (3) appears
**only** in the script. That is the fact that makes the fourth call necessary, and the
rationale on each count says so.

`excess` (9) is derived — 14 stuck against a threshold of 5 — and appears in neither
source, so it cannot be copied from anywhere.

## Grounding

`vendor/parsec/src/tools/icinga.py:97-104` gives the five accepted read actions;
`get_services`, `get_comments` and `get_downtimes` are three of them, and the
`detailed` and `host` arguments are declared in `sim-specs/icinga/openapi.json`. The
call sequence is the one 16 real traces use, in that order.

The `[Anarchy] Stuck AnarchySubjects` display-name shape and the
`monitoring/babylon/check_stuck_subjects.py` script path shape are both attested in the
trajectories as real monitoring artefacts; the file's contents here are authored.

The forbidden calls are `search_services` and `list_alerts` — the two actions
`icinga.py:122` rejects with `Unknown icinga action` and the two the observed agent
invented. Not any non-enum action: see `bench-v4-icinga-017` for why.

## A `type` field with no enum

`harness-skills/parsec-icinga/schema.json` emits `type` as a bare string on all four
entity kinds — the four `const` values in `sim-specs/icinga/openapi.json` are in
`LOST_IN_GENERATION`. The seed writes `"Service"`, `"Host"`, `"Comment"` and
`"Downtime"` exactly as the bundle's own `db.json` does, but nothing enforces it, so a
future seed saying `"host"` would be accepted. The contract, not the schema, is what
holds the line here.

## Weighting

`0.3 / 0.7`. The host and service are named in the instruction and so is the script
path, so no call is a discovery; the four-call sequence is still worth more than a
single given-id lookup, and the answer carries four independent facts.

## Invented

The stuck count 14, the thresholds 3 and 5, `STUCK_MINUTES = 30`, the script body and
every timestamp. **Nothing comes from the gitignored trace export.**
