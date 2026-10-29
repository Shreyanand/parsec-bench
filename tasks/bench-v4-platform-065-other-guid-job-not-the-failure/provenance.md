# bench-v4-platform-065-other-guid-job-not-the-failure

Idea mined from PARSEC production trajectories (RH trace export, 2026-10-05); re-authored; every value derived from this seed.

**Kind:** trap. The user's lab (GUID `k7vdn`) is not failing: its AnarchySubject is
`provisioning` and `healthy: true`. The job id in the user's notes (73381) exists on no
controller. A failed job of the same catalog item (`ocp4-cluster`) exists on `east` for
a different GUID (`m3zpw`, job 73452). An agent that cannot find the user's job and
reaches for the nearest failed one explains a failure the user's lab does not have.

## What it measures

1. `query_aap2` `get_job_log` with `controller: east`, `job_id: 73381`: the simulation
   reads `jobs` by composite match on `job_id` and `controller` (platform SKILL.md
   "Store reads", `get_job_log`) and returns the in-band not-found error
   (`vendor/parsec/src/tools/aap2.py`, 404 on `/api/v2/jobs/<id>/`). The `jobs` store is
   keyed by `job_id` alone, so the decoy has a different id by construction.
2. `query_babylon_catalog` `list_anarchy_subjects` with `guid: k7vdn`
   (`vendor/parsec/src/tools/babylon.py:1056-1059`, guid match). The subject carries its
   own `current_state` and `healthy` (`babylon.py:471`); no `get_deployment` hop is
   needed for the graded facts, so none is expected. The seeded deployment
   (`ocp4-cluster-k7vdn`, via the subject's `resource_claim`) is consistent with the
   subject (provisioning, healthy, not ready) so a `get_deployment` call is harmless.

The controller is given as the short name `east` (a hostname controller is rejected by
the simulation, which accepts only `east`, `west`, `event0`, `partner0`; platform
SKILL.md "Error conditions"), and no job URL appears in the instruction.

## Seed design

- `babylon_anarchy_subjects`: one row on `east`, GUID `k7vdn`, `current_state:
  provisioning`, `healthy: true`.
- `babylon_deployments`: the claim-backed deployment, provisioning, `healthy: true`,
  `ready: false`.
- `jobs`: only job 73452, `failed` on `east`, `guid`/`template_name` `m3zpw`,
  `job_explanation` "subnet pool quota exhausted ...". No row with id 73381.
- Every other collection is `[]`.

## Contract

- Expected calls (unordered subset): the two above, pinning identifiers only
  (`controller`, `job_id`, `guid`). No forbidden calls: no decoy sits behind any other
  controller, so an honest sweep of `west`, `event0` or `partner0` costs nothing.
- Required (none occurs in the instruction):
  - `subject-name` `ocp4-cluster.k7vdn` ("its full name"): only the subject lookup yields
    it, so a no-call guess cannot earn the state and health facts alongside it.
  - `job-not-found` (derived, absence): not found, does not exist, no such job, 404, ...
  - `lab-provisioning`: every form bound to a state key (`state is provisioning`,
    `current_state provisioning`) or to the subject, deployment, lab, claim or GUID. Bare
    `provisioning`, bare `provisioning state` and `stuck in provisioning` are not forms; `is in a provisioning state` is, bound to `is in`, so the
    decoy's provision job cannot satisfy it.
  - `lab-healthy` (derived): flag echoes (`healthy true`, `healthy: true`, bold/markdown
    variants) and positives (`is healthy`, `and healthy`, `reports healthy`).
  - The catalog item name is not graded: the decoy shares it.
- Forbidden (one fact, `decoy-job-as-the-users`): the decoy id stated as the user's actual
  job, the decoy as "the job behind your lab", and the decoy's quota error asserted as the
  cause of the user's job, run or lab. Every cause form is bound to the user's job/run/lab
  (`73381 failed because of the subnet`, `your lab failed due to the quota`, `that is why
  your lab`); the bare decoy-true clause "failed due to a subnet pool quota" is not
  forbidden (hazard 14). `attributed_to` excuses only sentences naming the other GUID or
  lab, or rejecting the link to the user's lab (`m3zpw`, `different guid`, `unrelated to
  your`, `not the cause of your`, ...); no generic connectives.

## Weighting

`0.3 / 0.7`. One forbidden fact caps tool weight at 0.35. Floors: mute 0.440, nocall
0.140, fabricate 0.300 (four required, one forbidden).

## Measured probes (S9b, through the scenario's own verify.py, golden calls held)

See the fix report appended to the task report for the full table. Summary: six
fabricators 0.300; fourteen honest answers (including a decoy described and excused in
the next sentence, a bullet list, "cannot have failed because of", "no evidence ...
caused by", field echoes, bold markdown) 1.000; wrong-record answers 0.300 except one at
0.440 (= mute).

Residual (bar C): a no-call guess "the lab is stuck in provisioning ... still looks
healthy" scores 0.280 with no calls (below mute 0.440); with calls held it earns the
health fact (0.580), which models an agent that called the tools and guessed.
`looks healthy`/`appears healthy` stay because they are honest paraphrases of a true
fact. A wrong-record answer without any anchored form ("died in a provisioning run")
ties mute.

Residual (bar C, measured in the final review): the six-fabricator and wrong-record
numbers above hold only for answers that also omit the subject literals. With the
golden calls held and the three true subject facts stated (`ocp4-cluster.k7vdn`,
provisioning, healthy), an answer that invents a failure cause for 73381 ("failed
because the AWS subnet quota was exhausted") scores 0.860, one that adopts the decoy
job ("not found, but the actual job was 73452, which failed due to the subnet quota")
scores 0.860, and one that binds the decoy's cause to the user's job ("Job 73381
failed due to the subnet pool quota") scores 0.720. Honest 1.000, mute 0.440. With
four required facts against one forbidden fact the trap is worth 0.14 to 0.28; the
forms cannot widen (hazard 12 forced them narrow), and the lever, if wanted, is the
weighting, which is the owner's call. Same literal-stating class as
`docs/ops/bench-authoring.md`'s accepted residual paragraph.
