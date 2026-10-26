# bench-v5-platform-109-quoted-false-is-truthy

## What it measures

A defined variable with the wrong *type*. The lab was ordered with GPU off, but
`vision_inference_gpu_enabled` reached the role as the string `"false"`. The log's
`debug var:` output shows it quoted. The MachineSet template tests it with a bare
`{% if vision_inference_gpu_enabled %}`, and in Jinja any non-empty string is truthy.
So the template rendered `replicas: 1` for a GPU pool nobody wanted, and the job then
exhausted 40 retries waiting for a GPU node to become ready.

The decoy is that machine-provisioning wait: the retry loop and its timeout, which a
teammate wants to lengthen. The AWS capacity decoy is deliberately not used, because
the challenge group (platform-113) has it.

## Grounding

- `query_aap2 get_job_log` (`west`, `647219`): composite `jobs` read.
- `fetch_github_file agnosticd/agnosticd-v2
  ansible/roles_ocp_workloads/ocp4_workload_vision_inference/templates/machineset-gpu.yaml.j2`,
  `ref` omitted. Seeded under `HEAD` and `main`, along with the role's
  `tasks/workload.yml`.
- **Path derivability:** the log's `task path:` lines name the role directory, and the
  tasks file names `template: machineset-gpu.yaml.j2`, which is the standard
  `templates/` location. The `task path:` numbers (2, 6, 11) are the seeded `- name:`
  lines, computed by `gen_109.py`.

## Contract

- Expected calls: ordered-subsequence, log then template. Weights 0.3/0.7. No forbidden
  calls and no citation item (the golden answer cites line 9 anyway).
- Required:
  - `string-false`: the quoted value in the log's debug output.
  - `truthy`: derived. The template test against the string.
  - `bool-fix`: `| bool` or an unquoted boolean.
- Forbidden fact `timeout-fix`: "increase the retries", "longer timeout", "slow to
  provision" and similar. No `attributed_to`; the golden answer dismisses the wait
  without those forms.

## The wrong answer

> readyReplicas 0 of 1 after 40 attempts. GPU nodes are slow to provision ... increase the
> retries (or use a longer timeout).

`score.py --golden-calls` gives **0.30** (answer 0.0). It misses all three required
facts and hits `timeout-fix`.

## Invented

Every literal is invented for bench-v5: job 647219, GUID `m6zjc`, the role
`ocp4_workload_vision_inference`, the MachineSet name and infra id, the variable names,
the catalog item and the git revision.

## Gate exemptions

- expected-call-underivable: fetch_github_file.path=ansible/roles_ocp_workloads/ocp4_workload_vision_inference/templates/machineset-gpu.yaml.j2 — the role's tasks file names the template: the job log's task path `/runner/project/ansible/roles_ocp_workloads/ocp4_workload_vision_inference/tasks/workload.yml` gives the role directory once the AAP project root `/runner/project/` is stripped, the golden `fetch_github_file` of that `tasks/workload.yml` (seeded under `HEAD` and `main`) returns the "Create the GPU MachineSet" `kubernetes.core.k8s` task with `template: machineset-gpu.yaml.j2`, and a role-relative template resolves from the role's `templates/` directory (Ansible role layout); the repo `agnosticd/agnosticd-v2` is the job's `git_url`.
