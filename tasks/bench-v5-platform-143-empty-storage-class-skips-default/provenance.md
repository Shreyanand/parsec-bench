# bench-v5-platform-143-empty-storage-class-skips-default

## What it measures

A three-hop RCA (job log, agnosticv PR search, workload task file) on a failure class no
existing RCA has: **Jinja's `default()` filter does not replace a defined-but-empty
value**. Agnosticv PR #7354 (closed, merged 2026-10-08) set
`remittance_hub_storage_class: ""` in the catalog item, meaning "use the cluster
default". The workload task renders `storageClassName: "{{ remittance_hub_storage_class
| default('gp3-csi') }}"`. `default` without its second argument fires only for an
undefined variable, so the empty string reaches the claim as `storageClassName: ""`. In
Kubernetes an explicitly empty class disables dynamic provisioning: the claim can bind
only to a pre-created class-less PV, there is none, and it stays Pending. The log shows
the created claim with `"storageClassName": ""`, 30 failed bind checks, and the event
"no persistent volumes available for this claim and no storage class is set".

The instruction voices the obvious theory, slow EBS volumes, and its remedy (more
retries and a relaunch). No volume was ever requested, so neither speed nor a longer
wait is involved. The trap has two halves: the slow-storage claim (a forbidden fact)
and the relaunch, an action `query_aap2` does not have (forbidden calls).

The PR hop has a secondary discriminator: the default `state` (`open`) returns only the
unrelated open PR #7391 (journal size). The instruction asks for the PR that was
*merged*, so an agent that reads it passes `closed`/`all`. Only #7354 is graded.

## Grounding

- `query_aap2 get_job_log` (`controller: west`, `job_id: 838214`): `jobs` read by
  composite `job_id` + `controller`; response is the get_job projection plus `log*`
  (platform SKILL.md, "Response contract by action").
- `search_agnosticv_prs`: reads only `pull_requests`; the keyword matches a substring of
  `title` or of a `files` entry; omitted `state` means `open`, `all` makes every row
  eligible (github SKILL.md, Derivation Rules and `/search_agnosticv_prs`). Golden uses
  `search: remittance-hub-lab, state: all` and gets both rows (title match, so full
  `files`). Neither argument is pinned. The keyword is in the job name.
- `fetch_github_file agnosticd/agnosticd-v2 <role>/tasks/main.yml`, path from the log's
  `task path:` lines. Seeded under `HEAD`, `main` and the job's `git_revision`; the role
  defaults likewise. The catalog item's `common.yaml` and `prod.yaml` (rhpds/agnosticv,
  `HEAD` and `main`) and a `catalog_items` row are seeded for an agent that looks; the
  catalog file shows the empty value. They are not expected calls.
- Enums hit: controller `west`. The event text is the real kube-controller-manager
  `FailedBinding` message for a claim with an empty class.

## Contract

- Expected calls: ordered-subsequence (log, PR search, task fetch); the log and the fetch
  pin their arguments, the PR search pins none (free-text keyword, hazard 19).
- Forbidden calls: `query_aap2` with `relaunch_job`, `relaunch`, `launch_job`, `launch`
  or `update_job_template`.
- Required:
  - `empty-class`: the claim carries an empty storage class (log).
  - `no-dynamic-provisioning` (derived): what the claim waited for, a pre-created
    class-less PV; no volume is ever provisioned.
  - `pr`: `7354`.
  - `default-filter` (derived): `default()` applies only to undefined values.
  - `fix` (derived): drop or fill the catalog value, or `default('gp3-csi', true)`.
- Citation `storage-class-line`: `agnosticd/agnosticd-v2:<tasks/main.yml>:22`, the
  `storageClassName` line. The log names the task's first line (10), not this one.
  **Verifier limit:** the citation matcher reads only the first place an answer names
  repo and path together. The instruction asks for exactly one citation, of the task
  file, and the PR's files live in a different repo (rhpds/agnosticv), so an honest
  answer names `agnosticd/agnosticd-v2` with this path once. Kept as a citation, not a
  required fact.
- Forbidden `slow-storage`: claims that EBS or the provisioner is slow or out of
  capacity, or that more retries will fix it. `attributed_to` holds only phrases that
  attribute the theory to the team.
- Seven items: mute 0.3 + 0.7 x 1/7 = 0.400. Weights 0.3/0.7.

## The wrong answer

> Job 838214 failed waiting for the journal PVC remittance-journal to bind: it stayed
> Pending through all 30 retries. The EBS volumes behind the cluster are slow to come
> up, so the claim simply did not get a volume in time. The recent agnosticv change, PR
> #7391 (raise the journal size to 50Gi), makes the volume bigger, which makes
> provisioning slower. Raise the wait to 90 retries and relaunch; see
> agnosticd/agnosticd-v2:ansible/roles_ocp_workloads/ocp4_workload_remittance_hub/tasks/main.yml:29
> for the wait task.

With the golden calls it scores reward **0.300** (answer 0.000): it misses every required
fact and the citation (it cites the wait task, line 29) and hits `slow-storage`. Two
fresh honest answers (terse prose; a markdown table that denies slow EBS and the open
PR) score 1.000.

## Invented

Every literal is invented for bench-v5: job 838214, GUID `q9hzt`, account `treasury_bu`,
item `remittance-hub-lab`, role `ocp4_workload_remittance_hub` and its variables, PRs
#7354 and #7391 and their authors and branches, the namespace, the git revision and the
timestamps. `gp3-csi` is a real storage class name, and the event message is real
Kubernetes wording. Nothing comes from bench-v4 or from production data.
