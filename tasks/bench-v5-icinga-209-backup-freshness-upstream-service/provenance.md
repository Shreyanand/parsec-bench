# bench-v5-icinga-209-backup-freshness-upstream-service

**Kind:** happy. **Services:** icinga, github. **Calls:** 3. **Weights:** 0.3 / 0.7.

## What it measures

A three-hop chain where a check script leads back into Icinga on a *different host*.
`wal-archive-freshness` on `pg-archive-01` is CRITICAL because a marker file is 31 h old.
The service's `vars.plugin` names `plugins/storage/check_marker_age.sh`. The script reveals
two things: the warning default (26 h, which appears only in the script), and that the
marker is written by the `pg-basebackup` service on `pg-primary-ord-1`. That service is hard
CRITICAL since 2026-11-17 21:52, and its output names the real fault (`max_wal_senders`
exhausted). An agent that stops at the alerting host blames the archive box.

## Grounding

- icinga: `get_services` with `host` reads `services` filtered by exact `attrs.host_name`, and
  rows are returned verbatim (SKILL.md). `vars` is an ordinary Icinga2 attribute inside
  `attrs`.
- github: `fetch_github_file` reads `files` by owner/repo/path/effective ref. The ref defaults
  to the repository default branch, so the file is seeded under both `HEAD` and `main`, as
  AUTHORING.md requires. The golden call omits `ref`, as the instruction does not give one.
- `rhpds/rhdp-monitoring` is on leakage.py's shared-system allow list. The path is new.
- No forbidden calls (not one of the group's eight).
- Validator WARNs, justified: golden calls 0 and 2 return the documented serialized
  `result` string. Every value inside it is a seed value.

## Contract

- Expected calls, `ordered-subsequence` (each depends on the previous one):
  `get_services host=pg-archive-01` → `fetch_github_file` of the plugin path →
  `get_services host=pg-primary-ord-1`.
- Required: `upstream-service` (pg-basebackup, in forms that the marker filename
  `.last_basebackup` cannot satisfy); `upstream-host`; `real-cause` (max_wal_senders, found
  only in the third result); `failure-start` (2026-11-17).
- Count: `warn-hours` 26 (script only).
- Forbidden: `blames-archive` (disk full, restart the archive).
  `attributed_to` holds only phrases that specifically refute or attribute this claim (see
  tests/expected.json). Generic words ("not", "only", "will", ...) are not used. The probe
  `.scratch/probe/209.md`, an asserting sentence that also contains a negation, is hit.
- Mute floor 1/6 = 0.17.

## The wrong answer

"... the archive job on pg-archive-01 has stalled ... Restart the archive service on
pg-archive-01 and check its disk", after only the first call (`.scratch/wrong/209.md`).
Reward 0.10: answer 0.0, tool calls 1/3.

## Invented

The hosts, services, marker path, script, outputs, addresses and epochs are invented for
this task. Nothing comes from bench-v4 or from production data.
