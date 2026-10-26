# bench-v5-platform-103-olm-channel-not-in-catalog

## What it measures

A two-hop RCA on a failure class no training RCA has: an OLM Subscription pinned to an
operator channel the catalog no longer publishes. The log carries three facts:

- the assert's `ResolutionFailed: constraints not satisfiable: no operators found in
  channel stable-3.2`;
- an earlier task's output listing the channels that do exist (`stable-3.4 stable-3.5`);
- the role's task path.

Only the role defaults name the variable that pins the dead channel
(`quarry_streams_channel`). The answer joins the two: the variable from the file, and
the replacement from the log. The plausible wrong reading blames OLM or the catalog
source.

## Grounding

- `query_aap2 get_job_log` (`east`, `560291`): a composite `jobs` read. The response is
  the get_job projection plus `log*`.
- `fetch_github_file agnosticd/agnosticd-v2
  ansible/roles_ocp_workloads/ocp4_workload_quarry_streams/defaults/main.yml`, with `ref`
  omitted, resolves to the default branch. It is seeded under `HEAD` and `main`, and so
  is `tasks/workload.yml`.
- **Path derivability:** the `task path:` lines name the role directory, and `git_url`
  names the owner and the repo. The `task path:` numbers (2, 9, 17) are the real
  `- name:` lines of the seeded `tasks/workload.yml`; `gen_103.py` asserts this.
- **Forbidden call:** any `fetch_github_file` against `agnosticd/agnosticd`, the legacy v1
  repository. The job's `git_url` names agnosticd-v2. This is the wrong-repository guard
  for this task, in the style of platform-003. It is not a wrong-owner trap.

## Contract

- Expected calls: ordered-subsequence, log then defaults. Weights 0.3/0.7.
- Required: `resolution-failed` is the log literal. `channel-var` comes from the file
  only. `available-channel` is derived: `stable-3.5` or `stable-3.4`, from the log's
  package-manifest output.
- Citation: line 9, `quarry_streams_channel: stable-3.2`, counted by `gen_103.py` from
  the seeded text.
- Forbidden fact `olm-blamed`: "catalog source is down", "OLM is broken" and similar. It
  has no `attributed_to`; the golden answer clears OLM without using those forms.

## The wrong answer

> ResolutionFailed: constraints not satisfiable. The community-operators catalog source is
> down or OLM is broken; restart the catalog pods.

`score.py --golden-calls` gives reward **0.44** (answer 0.2). It misses `channel-var`,
`available-channel` and the citation, and hits `olm-blamed`.

## Invented

Every literal is invented for bench-v5: job 560291, GUID `jr6tb`, the role
`ocp4_workload_quarry_streams`, the package `quarry-streams-operator`, its channels, the
catalog item and the git revision.

## Gate exemptions

- expected-call-underivable: fetch_github_file.path=ansible/roles_ocp_workloads/ocp4_workload_quarry_streams/defaults/main.yml — Ansible role layout: the `get_job_log` result's `task path` for "Create the operator subscription" is `/runner/project/ansible/roles_ocp_workloads/ocp4_workload_quarry_streams/tasks/workload.yml:9`, which names the role `ocp4_workload_quarry_streams` and its directory `ansible/roles_ocp_workloads/ocp4_workload_quarry_streams/` in the job's project; a role's defaults live at `<role>/defaults/main.yml`, the sibling of `tasks/`, and the instruction asks to "open the defaults of the role that created the subscription"; owner/repo `agnosticd/agnosticd-v2` is the same result's `git_url` (owner-approved 2026-10-13, convention case, `owner-decisions.md` 2b(4)).
