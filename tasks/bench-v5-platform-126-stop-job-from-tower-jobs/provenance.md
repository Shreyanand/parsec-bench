## What it measures

A happy two-hop chain from Babylon to AAP2. The agent has a GUID and a cluster, but no job id. It has to:

1. `query_babylon_catalog` `list_anarchy_subjects` `{cluster: heron}` (with `guid: m6qpz` or by picking the row from a cluster-wide listing). The subject's `tower_jobs` is keyed by lifecycle action. `stop` is `{controller: event0, job_id: 4419860}` and `provision` is `{controller: east, job_id: 4417203}`.
2. `query_aap2` `get_job` `{controller: event0, job_id: 4419860}`. The answer comes from status, finished time and `duration_seconds` (6444 s, about 1 h 47 m).

The hop uses the lifecycle key the user asks about (stop, not provision), and the controller comes from the same entry. The two jobs ran on different controllers.

## Grounding

- platform SKILL.md `/query_babylon_catalog`, Store reads: `list_anarchy_subjects` reads `babylon_anarchy_subjects` filtered by `cluster`. With a `guid`, a row matches on `instance_vars.guid`. Each subject carries `tower_jobs` "when stored". The schema types `tower_jobs` as "AAP2 job references keyed by lifecycle action".
- api.json: "A subject's `tower_jobs` is the hop to AAP2."
- `query_aap2` `get_job`: reads `jobs` by composite `job_id` + `controller`. The projection includes `status`, `finished`, `duration_seconds` and `action`. `event0` and `east` are values of the `QueryAap2Request.controller` enum. `cluster` is a free string in `QueryBabylonCatalogRequest`, so `heron` is a valid store key.
- Seeds: two subjects on heron, both carrying `cluster`; three jobs, unique `job_id`. The other GUID's stop (job 4419871) failed on the same controller and day. It is reachable only by guessing or by `find_jobs`, and none of its values satisfies a required form.

## Contract

- Calls, `ordered-subsequence`: `list_anarchy_subjects` pins only `action` (since 2026-10-25; it pinned `cluster` before), so a cluster-wide listing and the all-clusters GUID search both count. `get_job` pins `controller` and `job_id`, both from call 1's result.
- Forbidden call: `query_babylon_catalog` `action: get_anarchy_subject`. It is not an api.json enum value, and the in-band result is `Unknown action`. The singular is a plausible guess because `get_component`/`get_deployment` exist. A `get_job` on the provision job is a reasonable look and is not forbidden.
- Required: the job id 4419860, controller event0, the successful status, the finish time 18:49, and the duration. Duration is `derived`: 6444 s with honest phrasings.
- Weights 0.3/0.7.

## The wrong answer

An agent that stops after call 1 says: "The lab is stopped, so the stop worked; it's healthy." It names no job, controller or duration. An agent that follows `tower_jobs.provision` reports job 4417203 on east and its 77-minute run. `.scratch/probe/126-wrong.md` (the provision-job version, with the golden calls) scores **0.30**: answer 0/5. The mute-answer floor is 0.00 (0.30 with golden calls).

validate.py WARN, justified: `all (cluster-wide)` in golden call 0 is not a seed value. It is the documented literal for `namespaces_searched` when the request has no `namespace` (SKILL.md "Behavior by action", `list_anarchy_subjects`), so it is a derived envelope value.

## Invented

The GUIDs, job ids, names, email addresses, timestamps and the cluster `heron` are all invented. Nothing comes from bench-v4 or production data.
