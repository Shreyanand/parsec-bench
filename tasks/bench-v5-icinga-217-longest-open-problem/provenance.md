# bench-v5-icinga-217-longest-open-problem

**Kind:** happy. **Services:** icinga. **Calls:** 1. **Weights:** 0.3 / 0.7.

## What it measures

Ranking open problems by age. One `get_problems` call returns six non-OK rows: the DOWN host
`lims-scan-bru-4` and five services (`pg-vacuum-age` WARNING, `https-cert-days` WARNING,
`pg-follower-gap` CRITICAL, `scanner-spool` UNKNOWN, `tomcat-saturation` CRITICAL). The agent
must compare `last_state_change` across them and convert epochs against the stated "now"
(2026-11-25 07:00 UTC): the oldest is `pg-vacuum-age`, WARNING since 2026-11-13 05:30 UTC,
12 whole days; the newest is `tomcat-saturation` (06:20 that morning). The loudest rows
(CRITICAL, the host outage) are recent, so ranking by severity gives the wrong answer, and
counting only services gives 5 instead of 6.

## Grounding

- `get_problems` reads `hosts` and `services`, returns every stored row whose `attrs.state` is
  not OK, ignores all filters, and does not suppress acknowledged or downtimed rows (SKILL.md
  "Store reads", "Filtering rules for get_problems"). The seed's three OK rows (two hosts,
  `pg-backends`, `lims-web-ui`) are therefore absent from the golden result.
- `last_state_change` is the Icinga2 Checkable attribute stored in the free-form `attrs`.
- Leakage note: against the original v5 tasks the checker reports the field name
  `last_state_change` (used by 201-213). It is Icinga2 attribute vocabulary, not an entity
  identifier, and it is the field this task grades, so it stays. Against v4 the task is clean.

## Contract

- Expected call: `get_problems` (no arguments to pin).
- Required: `oldest` (pg-vacuum-age); `oldest-since` (2026-11-13, derived from the epoch,
  with a note); `newest` (tomcat-saturation).
- Counts: `total-problems` 6 (the host row plus five services); `oldest-days` 12 (derived,
  12 days 1.5 hours; `extra_any_of` "12 days", "12d", "12.1 days").
- Forbidden: `services-only-total` ("5 open problems", "total of 5 problems", ...). No
  `attributed_to`. Polarity checked: "There are not 5 open problems but 6" and a table cell
  `| 5 open problems | ❌ |` are not hits.
- Mute floor 0.417 (1 forbidden of 6 items, plus the 0.3 tool weight), nocall 0.117,
  fabricate 0.300.

## The wrong answer

The severity/services-only reading: "Icinga shows 5 open problems, all services ... The longest
open is pg-follower-gap ... about 2 days" (`/tmp/ext/scratch/bench-v5-icinga-217-longest-open-problem/wrong.md`).
Reward 0.533: answer 0.333. It names the newest correctly but misses the oldest, its date, both
counts, and hits the forbidden fact.

Three fresh honest answers (terse prose; a markdown table that denies the decoy; and bare
`Key: value` lines) all score 1.000.

## Invented

The hosts, services, outputs, addresses, certificate name and epochs are invented for this
task. Nothing comes from bench-v4 or from production data.
