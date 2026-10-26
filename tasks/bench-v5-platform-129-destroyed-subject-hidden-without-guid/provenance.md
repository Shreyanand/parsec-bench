## What it measures

Whether the agent knows that an absence in an unfiltered AnarchySubject listing is a projection rule, not a missing record. A colleague listed every subject on `condor` without a guid and concluded GUID `w2hcn` never existed. Destroyed subjects are omitted from such a listing. Calling `list_anarchy_subjects` with `guid: w2hcn` returns the subject as `destroyed`, along with its governor, requester and `tower_jobs` (provision 3301964, destroy 3308842, both on west).

The SKILL.md rule this rests on, quoted verbatim:

> platform SKILL.md `/query_babylon_catalog`, "Behavior by action", `list_anarchy_subjects`:
> "when `guid` is absent, omit rows whose `current_state` is `destroyed`"

api.json says the same in the operation's SIMULATION STORE AUTHORITY paragraph: "With a `guid`, an AnarchySubject row matches when its `instance_vars.guid` equals the guid or its `name` contains it; without a guid, subjects whose `current_state` is `destroyed` are omitted."

## Grounding

- `list_anarchy_subjects` reads `babylon_anarchy_subjects` filtered by `cluster`. With `guid`, a row matches when `instance_vars.guid` equals it or `name` contains it. Optional `resource_claim`, `requester_email` and `tower_jobs` are returned when stored.
- `cluster` is a free request string. All four seeded rows carry `cluster: condor`. The generator asserts that the guid-less listing does not contain the target, which is the colleague's view.
- A guid search with no cluster also works. The only stored cluster is condor, so the all-clusters path finds it there. That is why only `guid` is pinned.
- validate.py WARN (if shown), justified: `1` (count) and `all (cluster-wide)` are derived envelope values.

## Contract

- Call: `list_anarchy_subjects` pinned on `guid: w2hcn` only. The guid is the whole point, which is why the tool weight is 0.4.
- Required: `destroyed`, governor `ocp-ai-workshop`, requester `tfaleolo`, and destroy job `3308842`. The provision job is the other `tower_jobs` entry, and "the last lifecycle job" is the destroy.
- No forbidden facts: the 0.4 tool weight leaves no room in the mute floor, and the four required facts already separate the colleague's answer.
- Weights 0.4/0.6.

## The wrong answer

`.scratch/probe/129-wrong.md` agrees with the colleague after a guid-less listing on condor. It scores **0.15**: tool calls 0 (guid not used), answer 1/4 (only the governor, which leaks through the other subjects' names).

## Invented

The GUIDs, emails, job ids, names and the cluster `condor` are invented. Nothing comes from bench-v4 or production data.
