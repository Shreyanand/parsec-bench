# bench-v5-icinga-201-soft-critical-not-yet-hard

**Kind:** trap. **Services:** icinga. **Calls:** 1. **Weights:** 0.3 / 0.7.

## What it measures

Whether the agent reads Icinga's soft/hard state machinery instead of only `attrs.state`.
`pg-connections` on `pgw-ledger-03` is CRITICAL (`state` 2), but `state_type` is 0 (SOFT),
`check_attempt` is 2 of `max_check_attempts` 5, and `last_hard_state` is still 0. Icinga
notifies only on HARD states, so nobody has been paged. The agent has to say that, and work
out that 3 more failing checks are needed. At `retry_interval` 60 s that is about 3 minutes.
The trap is the `check_interval` of 300 s, which would give 15 minutes.

## Grounding

- api.json `/query_icinga` SIMULATION STORE AUTHORITY: `get_services` reads only `services`.
  The `host` filter matches `attrs.host_name` exactly, and rows are returned unchanged.
- SKILL.md Derivation Rules: "every returned field value equals the stored value verbatim".
  schema.json types `attrs` as a free object, so `state_type`, `check_attempt`,
  `max_check_attempts`, `retry_interval` and `last_hard_state` are stored and returned as seeded.
- Values follow real Icinga2 conventions: `state_type` 0 = SOFT, 1 = HARD; service state 2 = CRITICAL.
- The forbidden actions `get_state_history` and `get_notifications` are neither enum values
  nor documented aliases. The simulation answers them with `Unknown icinga action: <action>`.
  They are what a user asking "has it notified" invites.
- Validator WARN, justified: the golden result is the JSON *serialization* of the seeded
  rows (the documented `{"result": "<JSON string>"}` envelope). The grounding check compares
  the whole string against seed leaves, so it cannot find it. Every value inside the string
  is a seed value. Training tasks 045/046 carry the same WARN.

## Contract

- Expected call: `query_icinga {action: get_services, host: pgw-ledger-03}`. The host is
  pinned because it is given and is the point of the read.
- Required: `soft-state` (the word "soft" appears only in a correct reading of `state_type`);
  `not-notified` (derived, because no field says "not notified").
- Counts: `attempts-left` 3 (derived 5 - 2), `current-attempt` 2 (accepts "2/5", "2 of 5"),
  `minutes-to-hard` 3 (derived from `retry_interval`).
- Forbidden: `claims-hard-or-paged` ("hard critical", "already notified", "15 minutes", ...).
  `attributed_to` holds only phrases that specifically refute or attribute this claim (see
  tests/expected.json). Generic words ("not", "only", "will", ...) are not used. The probe
  `.scratch/probe/201.md`, an asserting sentence that also contains a negation, is hit.
- Weights 0.3 / 0.7: the single call is given, but the action choice is open (two invented
  actions are forbidden). Mute floor 1/6 = 0.17.

## The wrong answer

"Yes, wake the DBA. It's a hard CRITICAL, 188 of 200 slots, Icinga has already notified
the on-call; the next check is in 5 minutes." (`.scratch/wrong/201.md`). Its reward with the
golden calls is 0.30: answer 0.0, every required item and count missed, and the forbidden
fact hit.

## Invented

The host, the services, the address, the group, the outputs, the perfdata and every epoch
are invented for this task. Nothing comes from bench-v4 or from production data.
