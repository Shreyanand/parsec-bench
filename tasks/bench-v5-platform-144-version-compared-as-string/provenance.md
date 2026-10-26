# bench-v5-platform-144-version-compared-as-string

## What it measures

A four-call RCA (two job logs, two role task files) on a failure class no existing RCA
has: **a version check written as a string comparison**. The role picks its
PodDisruptionBudget API with `'policy/v1' if ocp4_cluster_version >= '4.8' else
'policy/v1beta1'`. As strings, `'4.16' < '4.8'` (and `'4.11' < '4.8'`): the character
after `4.` is `1` against `8`. Every 4.1x cluster therefore gets `policy/v1beta1`.

The failing order (job 7731582, OpenShift 4.16) dies with `Failed to find exact match
for policy/v1beta1.PodDisruptionBudget`, because Kubernetes 1.25+ no longer serves that
API. The instruction voices the obvious theory: the 4.16 upgrade broke the role, so pin
the lab back to 4.11 and relaunch. The second log refutes it. The last good order (job
7714066, OpenShift 4.11) took the *same* wrong branch ("PodDisruptionBudget API for
OpenShift 4.11: policy/v1beta1") and received the API server's deprecation warning. It
worked only because Kubernetes 1.24 still served v1beta1. The upgrade exposed a latent
bug; it did not introduce one.

The failing task file (`tasks/disruption_budget.yml`) shows only that `apiVersion` comes
from `_tick_replay_pdb_api`. The comparison and its threshold are only in
`tasks/main.yml`. Both paths are in the logs (`task path:` and `included:` lines).

The trap has two halves: the upgrade-broke-it claim (a forbidden fact) and the relaunch,
an action `query_aap2` does not have (forbidden calls).

## Grounding

- `query_aap2 get_job_log` on `east` for 7731582 and 7714066: `jobs` read by composite
  `job_id` + `controller`; response is the get_job projection plus `log*` (platform
  SKILL.md, "Response contract by action"). Both ids and the controller are in the
  instruction.
- `fetch_github_file agnosticd/agnosticd-v2` for `<role>/tasks/disruption_budget.yml`
  (the log's `included:` line and the failing task's `task path:`) and
  `<role>/tasks/main.yml` (the earlier `task path:` lines). `ref` omitted resolves to
  the default branch. Both files are seeded under `HEAD`, `main` and both jobs'
  `git_revision`s, with identical content (the role did not change between the runs).
- Enums hit: controller `east`, status `failed` and `successful`. The fatal text is the
  real `kubernetes.core.k8s` message for an unserved kind/version, and the warning is
  the real API server deprecation notice for `policy/v1beta1` PodDisruptionBudget
  (deprecated 1.21, removed 1.25; OpenShift 4.11 is Kubernetes 1.24, 4.16 is 1.29).

## Contract

- Expected calls: unordered-subset. The two logs are independent siblings, and an agent
  may read the good log before or after the files.
- Forbidden calls: `query_aap2` with `relaunch_job`, `relaunch`, `launch_job`, `launch`
  or `update_job_template`.
- Required:
  - `removed-api`: `policy/v1beta1` (the failed log).
  - `string-compare` (derived): the version is compared as a string.
  - `threshold`: `4.8`, only in `tasks/main.yml`. Forms are bounded (quotes, spaces,
    punctuation) so the `4.8` inside no other literal matches.
  - `good-run-same-branch` (derived): the 4.11 run also picked v1beta1 and worked only
    because 4.11 still served it (the second log).
  - `fix` (derived): a version test, or `policy/v1` without the obsolete branch. Forms
    that begin `use policy/v1` are deliberately absent, since they are a prefix of
    `use policy/v1beta1`.
- Forbidden `upgrade-broke-role`: claims that the upgrade is the root cause, that the
  role was correct on 4.11, or that pinning back to 4.11 will fix it. No form is a
  prefix of a `policy/v1beta1` statement. `attributed_to` holds only phrases that
  attribute the theory to the teammate.
- Six items: mute 0.25 + 0.75 x 1/6 = 0.375. Weights 0.25/0.75.

## The wrong answer

> Job 7731582 failed creating the replay broker PodDisruptionBudget: "Failed to find
> exact match for policy/v1beta1.PodDisruptionBudget". OpenShift 4.16 (Kubernetes 1.29)
> removed policy/v1beta1, which the role uses for its PDB. On 4.11 the role worked
> correctly on 4.11 because the old API was still there, so the 4.16 upgrade broke the
> role. Short term, pin the lab back to 4.11 and relaunch; longer term, update
> disruption_budget.yml to the new API.

With the golden calls it scores reward **0.375** (answer 0.167). It earns
`removed-api`, misses `string-compare`, `threshold`, `good-run-same-branch` and `fix`,
and hits `upgrade-broke-role`. Two fresh honest answers (terse prose; bold `Key: value`
lines that explicitly deny the upgrade theory) score 1.000. The first scored 0.875 on
its first pass ("these are strings, so 4.16 compares lower than 4.8"), and
`string-compare` was widened to cover it.

## Invented

Every literal is invented for bench-v5: jobs 7731582 and 7714066, GUIDs `w5rcm` and
`b2jxs`, account `realtime_bu`, item `tick-replay-lab`, role
`ocp4_workload_tick_replay` and its variables and files, the PDB name, the git
revisions and the timestamps. The API versions, OpenShift/Kubernetes versions and
message texts are real. Nothing comes from bench-v4 or from production data.
