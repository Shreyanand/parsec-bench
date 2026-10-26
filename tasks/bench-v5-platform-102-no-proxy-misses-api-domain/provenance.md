# bench-v5-platform-102-no-proxy-misses-api-domain

## What it measures

A two-hop RCA on a failure class no training RCA has: an egress-proxy exclusion list
that leaves out the cluster's own domain. The job log shows the kubernetes client's
`ProxyError ... Tunnel connection failed: 403 Forbidden` against the cluster API. That
error does not say which setting caused it. Only the role defaults show that
`meridian_gateway_no_proxy` covers `.svc` and `.cluster.local` but not
`.partner-labs.meridian.example`, so API traffic goes to the proxy, which refuses it.
The plausible wrong reading is that the partner's API server was down or had a
certificate problem.

## Grounding

- `query_aap2 get_job_log` (`controller: partner0`, `job_id: 417503`): a composite read
  on `jobs`. The response is the get_job projection plus `log*`. `partner0` is an
  api.json enum value.
- `fetch_github_file agnosticd/agnosticd-v2
  ansible/roles_ocp_workloads/ocp4_workload_meridian_gateway/defaults/main.yml`, with
  `ref` omitted, resolves to the default branch. The file is seeded under `HEAD` and
  `main`, and so is the role's `tasks/workload.yml`.
- **Path derivability:** the log's `task path:` names
  `/runner/project/ansible/roles_ocp_workloads/ocp4_workload_meridian_gateway/tasks/workload.yml`,
  and `git_url` names the owner and the repo. `defaults/main.yml` is the standard role
  layout, and the instruction asks for the role's defaults. The `task path:` line
  numbers (2, 7) are the real `- name:` lines of the seeded tasks file; `gen_102.py`
  asserts both.

## Contract

- Expected calls: ordered-subsequence, log then defaults fetch. Weights 0.3/0.7. No
  forbidden calls.
- Required: `proxy-403` is the log literal. `no-proxy-var` is the variable name, which
  is only in the file. `domain-missing` is derived: the comparison between the API host
  and the exclusion list.
- Citation: `agnosticd/agnosticd-v2:<defaults>:10`. `gen_102.py` computes the line from
  the seeded text.
- Verdict: `connectivity_failure`, exclusive, with a confidence.
- Forbidden fact `api-down` covers "API server is down" and "certificate". It has no
  `attributed_to`: the golden answer explains the cause without naming either reading,
  so any occurrence counts as an assertion.

## The wrong answer

> ProxyError, Tunnel connection failed: 403 Forbidden ... the cluster API server is down or
> rejecting connections, most likely a certificate or API availability issue.
> infrastructure_failure, medium.

`score.py --golden-calls` gives reward **0.4167** (answer 0.1667). It misses
`no-proxy-var`, `domain-missing`, the citation and the verdict, and hits `api-down`.

## Invented

Every literal is invented for bench-v5: job 417503, GUID `p7mzr`, the
`partner-labs.meridian.example` domain, the proxy host, the role
`ocp4_workload_meridian_gateway`, the catalog item name and the git revision.

## Gate exemptions

- expected-call-underivable: fetch_github_file.path=ansible/roles_ocp_workloads/ocp4_workload_meridian_gateway/defaults/main.yml — Ansible role layout: the `get_job_log` result's `task path` is `/runner/project/ansible/roles_ocp_workloads/ocp4_workload_meridian_gateway/tasks/workload.yml`, which names the role `ocp4_workload_meridian_gateway` and its directory `ansible/roles_ocp_workloads/ocp4_workload_meridian_gateway/` in the job's project; a role's defaults live at `<role>/defaults/main.yml`, the sibling of `tasks/`, and the instruction asks to "Read the role's defaults"; owner/repo `agnosticd/agnosticd-v2` is the same result's `git_url` (owner-approved 2026-10-13, convention case, `owner-decisions.md` 2b(4)).
