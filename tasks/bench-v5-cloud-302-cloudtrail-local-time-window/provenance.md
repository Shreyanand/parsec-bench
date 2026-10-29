# bench-v5-cloud-302-cloudtrail-local-time-window

**Kind:** trap. **Calls:** 1. **Weights:** 0.2 / 0.8.

## What it measures

Whether the agent converts a local-time window to UTC before it writes the `eventTime`
bounds of a CloudTrail Lake query. The user gives "between 09:00 and 10:30 Paris time" on
2026-09-03. Paris is on CEST (UTC+2) until 2026-10-25, so the window is 07:00-08:30 UTC.
In that window, rkovacs deleted 3 security groups in account 518306274913. Reading the
window as UTC (09:00-10:30Z) instead finds tbellamy's two DeleteSecurityGroup events
(09:18:52Z, 09:57:30Z, which are 11:18 and 11:57 in Paris). That pins the outage on the
wrong person with the wrong count. The instruction states only "Paris time"; the offset
is left implicit.

## Grounding

- cloud SKILL.md `/query_cloudtrail POST`:
  - Reads only `events`.
  - Column map: `eventTime -> event_time`, `eventName -> event_name`,
    `recipientAccountId -> account_id`, `userIdentity.username -> username`.
  - Aliased items are named by their alias.
  - The success body is `{columns, rows, row_count, bytes_scanned, truncated}`.
- api.json SIMULATION STORE AUTHORITY paragraph: "Timestamp comparisons compare instants".
  Stored `event_time` values are UTC (`Z`).
- The SQL is free text and is not pinned (expected call `query_cloudtrail` with `{}`), as
  in training.
- Seed `events`:
  - Target account: 3 DeleteSecurityGroup by rkovacs (07:12:44Z, 07:41:09Z, 08:06:27Z).
  - Also in the target account: 2 by tbellamy (09:18:52Z, 09:57:30Z), plus a
    DescribeSecurityGroups by rkovacs and an AuthorizeSecurityGroupIngress by tbellamy.
  - Decoy account 518306274931 (last two digits swapped): one DeleteSecurityGroup by
    nwiese at 07:30:16Z.
- **WARN justified:** `bytes_scanned` 41216 is the one computed scalar CloudTrail reports
  (SKILL.md: deterministic and positive when rows match). `eventName`/`eventTime` are
  column names taken from the SELECT list. None of them can be a seed value.

## Contract

- `actor` (required): rkovacs.
- `utc-window` (required, derived): states the UTC bounds or the +2 offset. None of the
  forms is in the instruction.
- `deletions` (count 3; nouns security groups / deletions / DeleteSecurityGroup /
  events / calls / groups). The wrong scopes give 2 (misread window), 5 (whole day) and 4
  (both accounts across 07:00-10:30 UTC).
- `blames-tbellamy` (forbidden): asserting tbellamy deleted, removed or broke things.
  The `attributed_to` phrases are specific to placing those events outside the window
  ("outside your window", "after the window", "read as UTC", ...). Probe
  `.scratch/wrong/p302.md` ("Outside of the obvious, tbellamy deleted the VPN group
  however.") is not excused: answer hit, reward 0.80.
- Floors: mute 0.25, echo 0.25.

## The wrong answer

`.scratch/wrong/w302.md`: queries 09:00-10:30 as UTC and reports "tbellamy deleted 2
security groups". With golden calls this scores reward **0.20** (answer 0.00): it misses
actor, utc-window and the count, and hits the forbidden fact.

## Invented

Every literal is invented: account ids, usernames, event ids, security-group ids and
times. Nothing comes from bench-v4 or from production data.
