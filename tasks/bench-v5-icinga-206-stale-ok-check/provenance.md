# bench-v5-icinga-206-stale-ok-check

**Kind:** trap. **Services:** icinga. **Calls:** 1. **Weights:** 0.2 / 0.8.

## What it measures

Whether the agent checks *when* a state was established before trusting it.
`restic-snapshot-age` on `bkp-vault-02` is `state` 0 with an OK output ("newest snapshot ...
is 5h old"). Its `last_check` and `execution_end`, however, are 2026-11-09 02:15 UTC, nine
days before the stated stand-up time (2026-11-18 08:00 UTC), and `enable_active_checks` is
false. The other two services on the host were checked within the last half hour, so the
host is being monitored and only this check stopped. The correct answer is that Icinga
cannot confirm last night's backup.

## Grounding

- `get_services` with `host` reads `services` filtered by exact `attrs.host_name`. Rows come
  back verbatim, including `last_check`, `enable_active_checks` and
  `last_check_result.execution_end` (SKILL.md Derivation Rules; `attrs` is free-form in
  schema.json).
- The forbidden actions `get_check_results` and `get_last_check` are neither enum values
  nor aliases.
- Validator WARN, justified: the golden `result` is the documented serialized string (as in
  training 045/046).

## Contract

- Expected call: `get_services` with `host: bkp-vault-02`.
- Required: `stale`; `active-checks-off`; `last-check-date` (2026-11-09); `cannot-confirm`
  (derived verdict).
- Count: `days-stale` 9. It is derived, and `extra_any_of` accepts "9 days", "nine days",
  "9d" and "over a week".
- Forbidden: `backup-ok` ("backup worked", "backups ok", ...).
  `attributed_to` holds only phrases that specifically refute or attribute this claim (see
  tests/expected.json). Generic words ("not", "only", "will", ...) are not used. The probe
  `.scratch/probe/206.md`, an asserting sentence that also contains a negation, is hit.
- Mute floor 1/6 = 0.17.

## The wrong answer

"Yes ... newest snapshot is 5h old, well inside the 26h warning threshold ... you can report
backups OK" (`.scratch/wrong/206.md`). Reward 0.20: answer 0.0.

## Invented

The host, services, outputs, thresholds, address, group and epochs are invented for this task.
Nothing comes from bench-v4 or from production data.
