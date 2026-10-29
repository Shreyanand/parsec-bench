# bench-v5-platform-105-failed-revision-not-main

## What it measures

Whether the agent checks *which code a failed job ran* before trusting the default
branch. The job's project was the `release-2026.08` branch at revision `71c0e4b…`. At
that revision the role's CRD manifest still declares
`apiextensions.k8s.io/v1beta1`, an API Kubernetes 1.22 / OpenShift 4.9 no longer serves.
On `main` the manifest is already `apiextensions.k8s.io/v1`, so the teammate's reading
of the default branch is accurate and beside the point. The job output is purged
(no stored `log`), so the only route to the cause is:

1. `get_job` (or `get_job_log`) for `git_branch` / `git_revision`;
2. a fetch at that revision.

**The discriminator is the revision-vs-main difference.** The required fact
`revision-api` (`v1beta1`) occurs only in the file content at the job's revision (and at
its branch, which points to the same content). It occurs nowhere on `main`, nowhere in
the instruction, and nowhere in the job metadata. An agent that reads only the default
branch cannot state it.

## Grounding

- `query_aap2`: the expected spec pins `controller: west` and `job_id: 804416` and
  leaves `action` unpinned, so either `get_job` or `get_job_log` satisfies it. Both read
  `jobs` by composite key, and both return `git_url`/`git_branch`/`git_revision` when the
  row carries them. The row has no `log`, so `get_job_log` returns `log: ""` with both
  sizes 0 (SKILL.md Derivation Rules). The golden path uses `get_job`.
- `fetch_github_file agnosticd/agnosticd-v2
  ansible/roles_ocp_workloads/ocp4_workload_ledger_policy/files/ledgerpolicy-crd.yaml`.
  It is seeded under `HEAD` and `main` (v1 content) and under the job's `git_revision`
  and `git_branch` (v1beta1 content). `ref` is not pinned in the expected call: fetching
  at the branch is an honest equivalent of fetching at the sha, and the answer component
  is what grades the revision read.
- The path is derivable: the instruction names the repository and the role. The
  manifest name follows the role's `files/` convention.

## Contract

- Expected calls: ordered-subsequence, the job metadata read then the manifest fetch.
  Weights 0.3/0.7. No forbidden calls.
- Required:
  - `revision-api`: revision only, the discriminator.
  - `which-revision`: the sha, the short sha or the branch, from get_job.
  - `api-removed`: derived.
  - `main-fixed`: derived. It reconciles the teammate's view.
- Forbidden fact `transient` (also "flaky", "just relaunch"). No `attributed_to`; the
  golden answer refutes the teammate without using those words.

## The wrong answer

> The manifest uses apiextensions.k8s.io/v1 with a proper versions list, so it is correct;
> the error was a transient API discovery hiccup; just relaunch.

`score.py --golden-calls` gives reward **0.30** (answer 0.0). It misses all four
required facts and hits `transient`. With a main-only fetch the tool component still
scores 1.0, so the answer component carries the whole discrimination, by design.

## Invented

Every literal is invented for bench-v5: job 804416, GUID `n3vqa`, the role, the CRD
group `ledger.fintrack.example`, the branch `release-2026.08`, the sha and the catalog
item.

## Gate exemptions

- expected-call-underivable: fetch_github_file.path=ansible/roles_ocp_workloads/ocp4_workload_ledger_policy/files/ledgerpolicy-crd.yaml — the role's tasks file names the manifest: the golden `fetch_github_file` of `ansible/roles_ocp_workloads/ocp4_workload_ledger_policy/tasks/workload.yml` (seeded under `HEAD`, `main`, the job's `git_revision` and `git_branch`) returns the "Create the LedgerPolicy CRD" `kubernetes.core.k8s` task with `src: ledgerpolicy-crd.yaml`, and a role-relative `src` resolves from the role's `files/` directory; the role `ocp4_workload_ledger_policy` and the repo `agnosticd/agnosticd-v2` are named in the instruction, and agnosticd-v2 keeps `ocp4_workload_*` roles under `ansible/roles_ocp_workloads/` (Ansible role layout: `<role>/tasks/workload.yml`, `<role>/files/`). The job output is purged, so that role directory is convention, not a literal any result shows (owner-approved 2026-10-13, `owner-decisions.md` section 3 platform-105 option (a)).
