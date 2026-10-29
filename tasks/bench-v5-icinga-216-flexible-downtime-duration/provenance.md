# bench-v5-icinga-216-flexible-downtime-duration

**Kind:** happy. **Services:** icinga. **Calls:** 1. **Weights:** 0.3 / 0.7.

## What it measures

Reading a *flexible* Icinga downtime correctly. The service downtime on `as2-inbox-files`
(host `edi-relay-lis-03`, CHG-58302, by `fmoreira-adm`) has `fixed: false`, a window
`start_time` 2026-11-21 22:00 UTC to `end_time` 2026-11-22 06:00 UTC, and `duration` 18000 s.
In Icinga2 a flexible downtime may begin anywhere inside its window (when the object goes into
a problem state) and then lasts `duration`, so alerts are muted for 5 hours, not for the 8-hour
window. The host also has an unrelated fixed host downtime (nsilvestre, CHG-58411, 2026-11-28),
so the agent has to pick the right row. The instruction states "now" (2026-11-21 15:00 UTC).

## Grounding

- `get_downtimes` reads only `downtimes`, filters by exact `attrs.host_name` (and
  `attrs.service_name` when `service` is given), ignores `search`/`filter_expr`/`detailed`,
  and returns rows verbatim (SKILL.md "Store reads", "Filtering rules"). A host-filtered call
  returns both downtimes; adding `service: as2-inbox-files` returns the graded one alone.
- `fixed` and `was_cancelled` are declared `IcingaDowntime.attrs` properties in api.json;
  `duration` and `entry_time` are Icinga2 Downtime attributes stored in the free-form `attrs`
  (the bundle's db.json carries `duration`). `start_time` < `end_time` is preserved as stored.

## Contract

- Expected call: `get_downtimes` with `host: edi-relay-lis-03`.
- Required: `flexible` (forms include `fixed: false`, present in the seed); `window-start`
  22:00 and `window-end` 06:00 (derived from the epochs, with notes); `author` (fmoreira-adm).
- Count: `muted-hours` 5 (`duration` 18000 s), with `extra_any_of` for "18000 s", "300
  minutes", "five hours", "5h".
- Forbidden: `window-as-duration` ("muted for 8 hours", "suppressed for 8 hours", "stay muted
  for 8", ...). No `attributed_to`. Polarity checked: "Alerts will not be muted for 8 hours" is
  not a hit; the honest table answer says "The 8-hour span is only the window ..." without
  hitting it.
- Mute floor 0.417 (1 forbidden of 6 items, plus the 0.3 tool weight), nocall 0.117,
  fabricate 0.300.

## The wrong answer

The fixed-downtime reading: "a scheduled maintenance window from 2026-11-21 22:00 UTC to
2026-11-22 06:00 UTC, so alerts will be muted for 8 hours, the whole window"
(`/tmp/ext/scratch/bench-v5-icinga-216-flexible-downtime-duration/wrong.md`). Reward 0.650:
answer 0.5. It gets the window and the author but misses `flexible` and the 5-hour count and
hits the forbidden fact.

Two fresh honest answers (terse prose; and a field/value table that explicitly denies the
8-hour reading) both score 1.000.

## Invented

The host, service, people, change numbers, comments, address and epochs are invented for this
task. Nothing comes from bench-v4 or from production data.
