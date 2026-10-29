# bench-v5-icinga-204-downtime-window-expired

**Kind:** trap. **Services:** icinga. **Calls:** 1. **Weights:** 0.2 / 0.8.

## What it measures

Comparing downtime windows against a stated "now" (2026-11-18 09:30 UTC, given in the
instruction). The user believes the host is in maintenance. Icinga has two downtimes for
`mq-relay-ams-1`, and neither covers 09:30. The first is a host downtime that ended on
2026-11-17 at 22:00. The second is a service downtime on `amqp-queue-depth` that starts on
2026-11-20 at 20:00. Both rows carry `is_in_effect: false`, and the future one has
`trigger_time` 0. The trap is to see "there are downtimes" and conclude that the host is
covered and the pages are expected.

## Grounding

- `get_downtimes` reads only `downtimes`. The `host` filter matches `attrs.host_name`
  exactly and returns host-level and service-level rows on that host (api.json SIMULATION
  STORE AUTHORITY, SKILL.md Filtering rules). That is why the service downtime on
  `amqp-queue-depth` comes back for a host-only request.
- `start_time`/`end_time`/`entry_time`/`trigger_time` are integer epochs, returned unchanged
  (SKILL.md Numeric Ranges: "preserve the stored ordering exactly"). `is_in_effect`, `fixed`
  and `duration` are Icinga2 Downtime attributes and are stored verbatim.
- The `services` row (CRITICAL, `downtime_depth` 0) is seeded for consistency only. The
  expected call does not read it.
- No forbidden calls (this task is not one of the group's eight).
- Validator WARN, justified: the golden `result` is the documented serialized string (as in
  training 045-048). Every value inside it is a seed value.

## Contract

- Expected call: `get_downtimes` with `host: mq-relay-ams-1`.
- Required: `not-covered` (derived verdict); `first-author` / `second-author`;
  `expired-end` (2026-11-17); `future-start` (2026-11-20).
- Counts: `on-record` 2; `hours-since-end` 11.5. The latter is derived, and `extra_any_of`
  accepts "11.5 hours", "11h30", "eleven and a half hours", and similar forms.
- Forbidden: `claims-covered` ("is in maintenance", "is covered by", "pages are expected").
  `attributed_to` holds only phrases that specifically refute or attribute this claim (see
  tests/expected.json). Generic words ("not", "only", "will", ...) are not used. The probe
  `.scratch/probe/204.md`, an asserting sentence that also contains a negation, is hit.
- Mute floor 1/8 = 0.125.

## The wrong answer

"Yes, mq-relay-ams-1 is covered by a downtime ... The host is in maintenance, so the pages
are expected noise" (`.scratch/wrong/204.md`). Reward 0.60: answer 0.5, because it reads
authors and dates correctly but misses the verdict, both counts, and the forbidden fact.

## Invented

The host, service, authors, change ids, comments, UUID-style names and epochs are invented
for this task. Nothing comes from bench-v4 or from production data.
