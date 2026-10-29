# bench-v5-cloud-310-stopped-lab-restarted-billing

**Kind:** trap. **Services:** cloud, platform, cost. **Calls:** 3. **Weights:** 0.3 / 0.7.

## What it measures

A three-service chain in which the owner's story ("stopped on 2026-09-28 and stayed
stopped") invites the conclusion that the stop failed. Two other sources refute it.

1. `query_aws_account_db {account_id: 645190837226}` gives sandbox5590 and GUID q7fwd.
2. `query_babylon_catalog list_anarchy_actions {guid: q7fwd}`, with no cluster, finds three
   actions on `apac-1`: provision (09-24), stop (finished 2026-09-28 18:06:12Z,
   successful) and **start** (finished 2026-10-01 07:51:03Z, successful).
3. `query_aws_costs` for exactly 2026-09-28..2026-10-05 (SERVICE) returns the daily series:
   - EC2 compute is 211.40 on 09-28, 0.00 on 09-29 and 09-30, 268.75 on 10-01, then
     331.20 a day;
   - the week's compute total is 1,473.75 USD;
   - EC2 - Other (EBS) is 130.20, for a total of 1,603.95.

The honest answer: the stop worked, the lab was started again on 2026-10-01, and that start
is what bills. The trap is answering "the stop failed / it ran all week / orphaned
resources" from the account DB and the cost total without reading the action history or
the per-day series.

## Grounding

- cloud SKILL.md `/query_aws_account_db POST`: with `account_id` and no `name`, it scans
  with an exact match. Envelope `{accounts, count, truncated}`.
- platform SKILL.md `/query_babylon_catalog POST`:
  - `list_anarchy_actions` with `guid` and no `cluster` searches each distinct stored
    `cluster` of `babylon_anarchy_actions` until one has a match.
  - A row matches when `subject_name` contains the guid.
  - The response is that cluster's `{cluster, actions, count, truncated,
    namespaces_searched: "all (cluster-wide)", errors: null}`.
  - Each action is projected to exactly `name, namespace, action, after, subject_name,
    subject_namespace, governor, state, finished`.
  - The other guid's actions (t2bxs) live on `emea-2` and are a leak sentinel.
- cost SKILL.md `/query_aws_costs POST`: resolves the `periods` row whose `start`/`end`
  equal the request dates exactly, then returns the stored `aws_cost_results` row for that
  `period_id` as stored. The seed row follows the SKILL.md example shape
  (`results[].groups[{key, amount, daily[{date, amount}]}]`, plus `ORG_TOTAL`).
- The instruction fixes both dates, so no end-date inference is involved. That is
  deliberately not training cost-073's end-exclusive trap.
- Expected calls (`unordered-subset`) pin `account_id`, `action` + `guid` (which forces the
  DB hop), and `account_ids` + both dates.
- **WARN justified:** `all (cluster-wide)` is the literal `namespaces_searched` value
  SKILL.md prescribes for a request without `namespace`. It is not seed data.

## Contract

- Required:
  - `guid`: q7fwd.
  - `start-action` (derived): a start or restart happened.
  - `resume-day`: 2026-10-01.
  - `stop-worked` (derived): the stop did not fail.
  - `compute-total`: 1,473.75. The 1,603.95 total_cost is a different figure.
- Forbidden `stop-blamed`: "the stop failed / did not take effect / never stopped / ran
  all week / orphaned resources". `attributed_to` is limited to framing the owner's claim
  ("whether the stop failed", "owner's theory that", "owner believes", "not that the stop
  failed"). Probe `.scratch/wrong/p310.md` ("Although the stop shows successful in
  Babylon, the stop failed for some instances.") is hit; reward 0.88.
- Floors: mute 0.17, echo 0.17.

## The wrong answer

`.scratch/wrong/w310.md`: "the stop failed and the instances kept running all week, so
there are orphaned resources", quoting 1,603.95. With golden calls: reward **0.42**. It
misses start-action, resume-day, stop-worked and compute-total, and hits the forbidden
fact.

## Invented

Every literal is invented: account ids, sandboxes, owners, GUIDs, governors, clusters,
action names, dates and costs. Nothing comes from bench-v4 or from production data.
