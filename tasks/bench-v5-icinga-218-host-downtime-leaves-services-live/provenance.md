# bench-v5-icinga-218-host-downtime-leaves-services-live

**Kind:** trap. **Services:** icinga. **Calls:** 1. **Weights:** 0.2 / 0.8.

## What it measures

Whether the agent reads a downtime's *scope*, per object, rather than taking "the host is in
downtime" to mean every alert on it is muted. Facilities put a host downtime on
`coldroom-plc-vlc-2` (13:00-17:00 UTC on 2026-12-09, CHG-71920) and the on-call lead says
nothing on the box can page. `get_services` for the host returns four services. Three are failing:

- `ups-autonomy` CRITICAL, `downtime_depth` 1: it has its own service downtime and is muted;
- `chiller-loop-temp` WARNING (glycol return 4.8 C), `downtime_depth` 0;
- `modbus-bridge` CRITICAL (no reply from 10.73.12.41:502 unit 7), `downtime_depth` 0.

An Icinga 2 host downtime puts only the host object in downtime. The services get one only if
service downtimes are scheduled too (the `all_services` option), and each service's own
`downtime_depth` says whether it has one. So two of the three failing services will still notify.
The trap is to answer "all covered, safe to silence the phone".

## Grounding

- `query_icinga` `get_services` with `host` reads `services` and keeps rows whose
  `attrs.host_name` equals it exactly; rows come back verbatim, ordered by name (SKILL.md "Store
  reads", "Filtering rules", On-Demand Generation Rules). Four rows here.
- `downtime_depth`, `state`, `state_type`, `enable_notifications` and `last_check_result` live in
  the free-form `attrs` and are returned unchanged.
- The `downtimes` collection holds the host downtime (`service_name` "") and the separate service
  downtime on `ups-autonomy`, so an agent that also calls `get_downtimes` with `host` sees
  the same picture: no downtime for `chiller-loop-temp` or `modbus-bridge`.
- Icinga 2 semantics: `Checkable::IsInDowntime` counts only the checkable's own downtimes, and the
  implicit service-to-host dependency suppresses service notifications only when the host is
  hard non-UP (it is UP here). The `schedule-downtime` API's `all_services` flag exists for exactly
  this reason.
- The forbidden actions `schedule_downtime` and `acknowledge_problem` are real Icinga 2 API
  *actions*, but they are writes, and `query_icinga` has neither (not a canonical action, not an
  alias). They are what "make it stop paging me" invites instead of reading.

## Contract

- Expected call: `get_services` with `host: coldroom-plc-vlc-2` (`ordered-subsequence`).
  Forbidden calls: `schedule_downtime`, `acknowledge_problem`.
- Required: `host-scope` (derived: the host downtime does not cover the services / they are not in
  downtime / they still notify); `chiller-detail` (4.8 C / glycol); `modbus-detail` (no reply /
  unit 7 / 10.73.12.41 / port 502).
- Count: `will-notify` 2 (nouns services/checks/alerts/problems/notify/page, window 4; pairs
  "2 of 3", "two of the three", "both still ..." in `extra_any_of`). Derived, with a note.
- Forbidden: `all-covered` (assertions that all failing services, or everything on the host, are
  covered; that the host downtime covers or is inherited by the services; that it is safe to
  silence the phone). No `attributed_to`. Polarity checked: "The host downtime does not cover its
  services", "Are all its alerts suppressed? No." and "Everything is covered: No." are not hits.
  Forms that an honest answer says of the covered UPS check ("covered by the host downtime",
  "safe to mute") were left out (hazard 14).
- Floors: mute 0.360, nocall 0.160, fabricate 0.200.

## The wrong answer

"coldroom-plc-vlc-2 is in an active downtime ... so the host downtime covers its services ... All
three are covered by the maintenance window, so it's safe to switch your phone to silent until
17:00 UTC." (`/tmp/ext/scratch/icinga-218-220/a/218-wrong.md`). Reward 0.200: answer 0.0 (it names
no failure detail, gives no count of 2 and trips `all-covered`). Two further fabricators phrased the
way the instruction invites ("you're fully covered ... all of its alerts are suppressed"; "The host
downtime covers the services on it") also score 0.200.

Two fresh honest answers (terse prose; and a markdown table plus `Key: value` line that denies
the host downtime covers everything) both score 1.000.

## Invented

The host, services, outputs, addresses, change number, downtime author and epochs are invented
for this task. Nothing comes from bench-v4 or from production data.
