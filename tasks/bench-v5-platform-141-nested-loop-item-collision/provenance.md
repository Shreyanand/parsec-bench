# bench-v5-platform-141-nested-loop-item-collision

## What it measures

A three-call RCA on a failure class no existing RCA has: **a nested-loop variable
collision**. `tasks/main.yml` creates one project per seat and then includes
`seat_access.yml` once per seat, both with the default loop variable `item`.
`seat_access.yml` loops over the roles, also with `item`. Inside the inner loop `item`
is the role, so each RoleBinding goes to `edit-t6bvz` / `view-t6bvz` instead of
`guild-user1-t6bvz`, and the API answers 404 `namespaces "edit-t6bvz" not found`.

The loud symptom (namespace not found, right after the projects were created) reads as
a race, and the instruction voices that theory with its remedy (a pause and retries).
The log refutes it twice: the seat projects were created (`changed` for all three
seats), and the missing namespaces are named after roles. Ansible's own warning, `The
loop variable 'item' is already in use`, sits a few lines above the failure. The two
task files show where the collision is: the outer loop in `main.yml` and the inner loop
and namespace line in `seat_access.yml`. Both paths come from the log's `task path:` and
`included:` lines.

## Grounding

- `query_aap2 get_job_log` (`controller: event0`, `job_id: 287455`): `jobs` is read by
  composite `job_id` + `controller`; the response is the get_job projection plus `log*`
  (platform SKILL.md, "Response contract by action").
- `fetch_github_file agnosticd/agnosticd-v2` for `ansible/roles_ocp_workloads/ocp4_workload_guild_seats/tasks/main.yml` and `ansible/roles_ocp_workloads/ocp4_workload_guild_seats/tasks/seat_access.yml`, with `ref`
  omitted, resolve to the default branch (github SKILL.md). Both files and the role's
  `defaults/main.yml` are seeded under `HEAD`, `main` and the job's `git_revision`
  `b47e0d29a6c13f58e2d9a0b71c4f36e8d5a2b90c`, identical content.
- **Path derivability:** both paths are substrings of the log's `task path:` and
  `included:` lines; owner and repo come from `git_url`. No exemption.
- Enums hit: controller `event0`. The warning text follows ansible-core's real wording.
- The citation line (12) is counted from the seeded `seat_access.yml` by the
  generator script (scratch, outside the task).

## Contract

- Expected calls: unordered-subset (the two fetches are siblings; every argument that
  matters is pinned).
- Forbidden calls: any `fetch_github_file` against `rhpds/agnosticd-v2` or
  `agnosticd/agnosticd`. The job's `git_url` names `agnosticd/agnosticd-v2`.
- Required:
  - `wrong-project`: a role-named namespace from the 404s.
  - `seats-created`: a seat project the first task created.
  - `collision`: the shared `item` between the two loops.
  - `fix` (derived): a distinct loop variable (`loop_control` / `loop_var`).
- Citation `namespace-line`: `agnosticd/agnosticd-v2:ansible/roles_ocp_workloads/ocp4_workload_guild_seats/tasks/seat_access.yml:12`.
- Forbidden fact `not-ready`: claims that the projects were not ready or not yet
  created, that it is a race, or that a pause or retries will fix it. `attributed_to`
  holds only phrases that attribute the theory to the teammate.
- Six items: mute 0.3 + 0.7 x 1/6 = 0.417. Weights 0.3/0.7.

## The wrong answer

> The RoleBindings failed with 404 namespaces "edit-t6bvz" not found. The projects
> weren't created yet when the bindings were applied, so this is a race condition
> between project creation and RBAC. Add a pause and retries (until the namespace
> exists) to the "Bind the seat user to its roles" task.

With the golden calls it scores reward **0.417** (answer 0.167). It earns
`wrong-project`, misses the rest and the citation, and hits `not-ready`. Three fresh
honest answers (prose, `Key: value` lines denying the race, and one refuting the
teammate's theory by restating it) score 1.000.

Measured residual: the verifier's citation matcher reads only the first occurrence of
`agnosticd/agnosticd-v2` + the `seat_access.yml` path. An honest answer that names that
file with its repo once *before* citing it with the line loses the citation (0.883). The
natural earlier mention in this task is `main.yml`, a different path, which does not
trigger it.

## Invented

Every literal is invented for bench-v5: job 287455, GUID `t6bvz`, account `devx_bu`,
item `pipeline-guild-workshop`, the role `ocp4_workload_guild_seats`, its files and
variables, the seat user names, the git revision and the timestamps. `edit` and `view`
are the standard Kubernetes ClusterRoles. Nothing comes from bench-v4 or from
production data.
