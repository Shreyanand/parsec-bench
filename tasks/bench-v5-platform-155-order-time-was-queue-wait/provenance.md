## What it measures

Splitting an order's elapsed time into **queue wait** and **run time**, which needs one field
from each of two sources. The partner says the lab took about 75 minutes and blames the
playbook.

- `query_aap2 get_job` on partner0/8217744: `successful`, `started` 14:51:37, `finished`
  15:19:05, `duration_seconds` 1648. The playbook ran 27 min 28 s, inside the 30-minute promise.
- `query_splunk search_aap2_logs` on partner0 (by GUID or job id): awx.main.scheduler logged the
  job **created pending at 14:04:12**, then twice "insufficient capacity (job needs 6 forks, 0 of
  144 available; 24 jobs running in the group)" for instance group `velo-partner-ee`, then
  "submitted to execution node exnode-lyo-07" at 14:51:36.

The wait (47 min 25 s) is in no field: it is the log's creation time subtracted from the job's
start. The node is in no AAP2 field either.

**Kind: happy.** Both calls succeed and the evidence is unambiguous. The partner's theory is a
guard (one forbidden fact), not the point.

## Grounding

- platform SKILL.md "/query_aap2": `get_job` reads `jobs` by `job_id` + `controller` and
  returns the documented projection (no execution node, no creation time).
- platform SKILL.md "/query_splunk": `search_aap2_logs` requires `controller`, reads only
  `splunk_aap2_log_entries`, matches rows where the requested strings occur anywhere in the row
  as raw text, projects time/controller/level/logger/message, and builds
  `index=federated:rh_pds-001_aap "<controller>" "<guid>" | spath | sort -_time` (results newest
  first). Every seeded row contains `partner0` (its controller field), the GUID and the job id,
  so a search by guid or by `search_terms: 8217744` returns the same six rows. The instruction
  gives the date, so a correct `earliest`/`latest` covers it.
- Seed: `jobs` 1, `splunk_aap2_log_entries` 6.

## Contract

- tool_calls (0.3), unordered-subset (the GUID and job id are both in the instruction):
  `query_aap2` {controller: partner0, job_id: 8217744} (action unpinned: `get_job` or
  `get_job_log` both carry `started` and `duration_seconds`) and `query_splunk`
  {action: search_aap2_logs, controller: partner0}. The search's guid, search terms and window
  are unpinned.
- answer (0.7), `fold_markup` on: required `exec-node` (exnode-lyo-07), `capacity` (derived:
  the scheduler's reason) and `instance-group` (velo-partner-ee). Counts `run-minutes` (27,
  with 1648 s / 27.5 / 27:28 forms) and `wait-minutes` (47, with 47:25 / 2845 s forms), both
  derived. Forbidden `playbook-slow` (the partner's theory, stated as a claim; a denial such as
  "the playbook was not slow" is excused by polarity, and `attributed_to` excuses a sentence
  that names the theory as the partner's, e.g. "the partner thinks the playbook was slow").
- Items: 6. Mute 0.3 + 0.7 x 1/6 = 0.417.

## The wrong answer

"The job ran for about 75 minutes (14:04 to 15:19), so the playbook itself was slow; it finished
successfully. I'd review the provisioning roles for regressions." With the golden calls it scores
**0.300** (answer 0.0: every required fact and both counts missed, the forbidden fact hit).
A subtler wrong answer that reads only `get_job` ("the playbook ran 27.5 minutes, so the rest must
be the partner's side; I can't tell which node") scores 0.533. Two fresh honest answers (terse
prose, and `Key: value` lines denying the slow-playbook theory) score 1.000.

## Invented

Every literal is invented: the partner name, GUID, job id, job and template names, instance
group, execution node, fork figures and times. `partner0` is a controller name from the api.json
enum. Nothing comes from bench-v4 or from production data.
