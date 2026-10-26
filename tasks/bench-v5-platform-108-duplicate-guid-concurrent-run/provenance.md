# bench-v5-platform-108-duplicate-guid-concurrent-run

## What it measures

A CloudFormation `AlreadyExistsException` whose cause is a second, still-running
provision for the same GUID. The log alone suggests a leftover stack. The answer needs
three reads:

- `find_jobs`, which shows the sibling 512937 `running` alongside the failed 512944;
- the job log, for the error;
- the config's ec2 defaults, which show `stack_name: "{{ env_type }}-{{ guid }}"`. A
  name built from the GUID alone makes two runs for one GUID collide by construction.

The instruction also asks the agent to stop the other run, which `query_aap2` cannot
do.

## Grounding

- `get_job_log` (`west`, `512944`): composite `jobs` read.
- `find_jobs` (`controller: west`, `template_name: h8cuy`): keeps rows whose `job_name`
  contains `h8cuy` case-insensitively and orders by `finished` descending. The running
  sibling has `finished: ""` (schema: "empty when unfinished"), so it sorts after the
  failed run. The unrelated `x4pzd` job (same template, other GUID, successful) is
  excluded. `total` = 2.
- `fetch_github_file agnosticd/agnosticd-v2 ansible/configs/iot-fleet-sim/default_vars_ec2.yml`,
  seeded under `HEAD` and `main`. The config name is in the stack name and the job name,
  and `default_vars_ec2.yml` is the per-provider defaults convention the instruction
  points at.
- **Forbidden calls:** `query_aap2` `action` `cancel_job`, `cancel` or `stop_job`. None
  is in the api.json action enum.

**Deviation from the design.** The design pinned `absent_args: ["status"]` on the
expected `find_jobs`. I dropped it: `status: running` is an honest way to find the
sibling and would have been rejected. The expected call pins only
`action: find_jobs`. The `sibling-job` and `sibling-running` facts carry the
discrimination; a `status: failed` search cannot supply either.

## Contract

- Expected calls: ordered-subsequence, log, then find_jobs, then defaults. Weights
  0.3/0.7.
- Required:
  - `already-exists`: from the log.
  - `sibling-job` (512937) and `sibling-running`: from find_jobs.
  - `guid-only-name`: derived, from the file.
- Count: `guid-jobs` = 2.
- Forbidden fact `wrong-cause`: "leftover stack", "orphaned stack", "previous failed
  run", "template bug", or naming `x4pzd`. No `attributed_to`.

## The wrong answer

> AlreadyExistsException ... 1 failed provision job for h8cuy ... a leftover stack from a
> previous failed run; delete the stack and relaunch.

With the golden calls: **0.4167** (answer 0.167). With the wrong transcript
(`find_jobs` with `status: failed`, then `cancel_job`): **0.1167**, because the
forbidden call zeroes the tool component.

## Invented

Every literal is invented for bench-v5: jobs 512944, 512937 and 512902, GUIDs `h8cuy`
and `x4pzd`, the config `iot-fleet-sim`, the stack name, instance sizing and the git
revision.

## Gate exemptions

- expected-call-underivable: fetch_github_file.path=ansible/configs/iot-fleet-sim/default_vars_ec2.yml — agnosticd config layout and stack naming: the `get_job_log` result's log fails on the stack `iot-fleet-sim-h8cuy` for GUID `h8cuy`, and agnosticd names a lab's CloudFormation stack `{{ env_type }}-{{ guid }}`, so the agnosticd config (agnosticd's `env_type`) is `iot-fleet-sim` (the fetched file confirms the convention: it carries `stack_name: "{{ env_type }}-{{ guid }}"`; that is post-hoc corroboration, not part of the route, since it is the file whose path is being derived); the job row's own `env_type` field is `prod` (the RHDP stage, as in the job name `RHDP iot_bu.iot-fleet-sim.prod-h8cuy-2-provision`), so parsec's `fetch_github_file` layout `ansible/configs/{env_type}/default_vars.yml` must not be filled literally from that field; the same row gives `cloud_provider: ec2`, and agnosticd keeps a config's per-provider defaults beside it as `default_vars_<cloud_provider>.yml`, which is what the instruction's "check the config's ec2 defaults" asks for; owner/repo `agnosticd/agnosticd-v2` is the same result's `git_url` (owner-approved 2026-10-13, convention case, `owner-decisions.md` 2b(4)).
