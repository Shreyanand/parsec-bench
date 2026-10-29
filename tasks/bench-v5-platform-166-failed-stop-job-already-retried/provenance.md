## What it measures

Reading an AAP2 failure against Babylon's own action history, from AAP2 to Babylon. A governor
owner holds an alert for failed job 8164305 on `partner0` and is about to page the lab's owner to
re-order. Two calls in a chain:

1. `query_aap2 get_job {controller: partner0, job_id: 8164305}`: `action: stop`, `guid: t5wqe`,
   failed at 2026-11-03T22:14:09Z because "1 of 3 hosts did not reach the stopped state". The
   alert reads like a failed order, but the job was a **stop**.
2. `query_babylon_catalog list_anarchy_actions {cluster: gannet, namespace:
   babylon-anarchy-amq-bridge-lab}`, using the **namespace filter** on the governor's namespace from
   the instruction. Out of six gannet rows, two are stop actions for `amq-bridge-lab.t5wqe`:
   - `-stop-h7pqz`, failed, finished 2026-11-03T22:14:20Z (the alerted job);
   - `-stop-r2kvd`, **successful**, finished 2026-11-04T00:09:47Z (Babylon's retry).

The honest answer: the job was a stop for t5wqe, there were 2 attempts, the second succeeded at
00:09 UTC, and nothing needs doing. Decoys: the provision of `n2hdc` failed in the same namespace
(another lab), and a failed stop of the same governor sits on another cluster (`booby`), which
cluster filtering removes. The retry's own AAP2 job (8164977, successful) is seeded so that an
agent that chooses to verify it can, but it is not required.

Behaviour: **an AAP2 job's `action` and `guid` matched to the governor's namespace-scoped
action history, where a later successful action of the same kind supersedes the failure.** One
count (attempts).

## Grounding

- platform SKILL.md `/query_aap2`, `get_job`: reads `jobs` by composite `job_id` + `controller`.
  The projection includes `action`, `guid`, `status`, `finished` and `job_explanation`; `id` is
  never returned. `partner0` is a `controller` enum value.
- platform SKILL.md `/query_babylon_catalog`, `list_anarchy_actions`: reads
  `babylon_anarchy_actions` filtered by `cluster`. "optional `namespace` narrows results", and then
  `namespaces_searched` is `[<namespace>]`. `errors` is `null`. Each action is projected to exactly
  `name`, `namespace`, `action`, `after`, `subject_name`, `subject_namespace`, `governor`, `state`
  and `finished`. parsec: `_list_anarchy_actions` (`vendor/parsec/src/tools/babylon.py:1303-1369`).
- Seeds: two jobs with unique `job_id`; seven action rows with unique ids, every one carrying
  `cluster`. List order in the golden result is by name.

## Contract

- Calls, `ordered-subsequence`: `get_job` pins `controller` and `job_id` (from the instruction).
  `list_anarchy_actions` pins `cluster` and `namespace` (from the instruction). A `guid` or `search`
  argument is allowed and unpinned.
- Required: the GUID `t5wqe` (only in the job); that it was a stop (forms `stop`, `shut down`,
  ...; the instruction never says stop); the retry's finish time `00:09` (only in the action
  rows).
- Count: 2 attempts (nouns attempts / stop actions / tries / times).
- Forbidden (`lab-still-up`): claims that the lab is still running or was never retried. The
  forms carry no `stop` substring (hazard 12).
- Weights 0.3/0.7. `fold_markup` on. Gate: golden 1.000, mute 0.440, nocall 0.140, fabricate
  0.300.

## The wrong answer

"Job 8164305 belongs to t5wqe. It failed because 1 of 3 hosts did not reach the stopped state, so
the lab is still running. Page the owner and stop it manually, or re-order it." Scores **0.580**
with the golden calls. It states two true literals (GUID, stop), so it gets partial credit (bar
C), but it misses the retry and the count and trips the forbidden fact. Three fresh honest answers
(terse prose; key/value plus a table that denies the lab is still running; prose that never uses
the word "stop" for the job) all score 1.000.

## Invented

The cluster names `gannet` and `booby`, the governor, namespace, GUIDs, action names, job ids,
explanation text and timestamps are all invented. `partner0` is an api.json enum value. Nothing
comes from bench-v4 or production data.
