# bench-v5-platform-111-recycled-sandbox-swallowed-teardown

## What it measures

A five-hop RCA in which the failing job is innocent. A provision dies with
`VpcLimitExceeded`; the cause is in the *history of the pooled sandbox account*: the
previous lease's destroy job failed to delete four VPCs (`DependencyViolation`, a
workload-created VPC interface endpoint), ignored those failures because the previous
catalog item sets `aws_vpc_teardown_tolerate_errors: true`, reported `successful`, and
returned the account to the pool dirty. The agent has to follow the lease line in the
first log to a different GUID, find that GUID's destroy job, read the failed events of
a job whose status is green, and read the previous item's config.

## Tranche

**Challenge.** Expected to score below 1.0 for a good agent. The agent failure it
exposes is **treating a failed job as self-contained and trusting a green status**:
the loud error has a ready-made remedy (raise the VPC quota), the lease line says the
previous cleanup "reported: successful", and the job that actually caused the failure
is `successful` — `find_jobs status=failed` never shows it. Only an agent that reads
the events of a successful destroy finds the four ignored failures, and only one that
then reads the *other* catalog item's config can name the setting. Single-hop agents
stop at the quota; careful agents commonly name the leftovers without the setting.

## Grounding

- `query_aap2 get_job_log` / `get_job_events`: platform SKILL.md "Store reads" — composite
  `job_id` + `controller` on `jobs` / `job_events`; events ordered by `counter`;
  `failed_only` keeps events whose stored `failed` is true (ignored failures are stored
  `failed: true`, as Ansible records them).
- `query_aap2 find_jobs`: `template_name` is a case-insensitive substring of stored
  `job_name`; the previous GUID `m2wqd` is in both `fleet-hub-lab` job names (provision
  and destroy), so the golden result returns both, `finished` descending. The GUID is
  derivable only from the first log's lease line, never from the instruction.
- `lookup_catalog_item`: the Babylon form `agd-v2.fleet-hub-lab.prod` (from the destroy's
  `job_name`) resolves through the `<item>` segment; returned `path` is the item's
  `prod.yaml`, which is where the setting lives (no composed path needed).
- `fetch_github_file`: rows seeded under both `HEAD` and `main`.
- Enum values: controller `east`.

## Contract

Weights 0.3 / 0.7. Calls `ordered-subsequence`; pinned only what the chain derives
(failing job, the destroy job id, the fetched path); `find_jobs` arguments are unpinned
so `m2wqd`, `fleet-hub-lab.prod-m2wqd` or a controller filter all pass.

- `previous-destroy` — job 3302265 / `m2wqd-destroy`: proves the agent left the failing job.
- `dependency-violation` — why the VPCs survived; only in the destroy's events.
- `tolerate-var` — the setting; only in the previous item's prod.yaml.
- `swallowed` (derived) — success status despite failed deletes.
- `dirty-reuse` (derived) — the failing lab inherited the leftovers.
- count `leftover-vpcs` = 4 (window 8).
- forbidden `quota-increase` (attributed_to excuses rejection sentences) and
  `failing-item-config` (blaming mesh-tracing-lab, which builds one VPC).

Mute answer floor: 2 forbidden of 8 graded items → answer 0.25, reward 0.475 with golden
calls (validate.py's answer-component threshold 0.45 is not exceeded).

leakage.py WARN (weak literals), justified: `fold_markup`, `ncloud_provider` are contract keys, logger/file names or standard AgnosticD variable names shared by the API's world (`ncloud_provider`-style tokens are `\n` + a key in serialized YAML), not scenario identity.

Excuses (2026-10-12 generic-excuse fix pass): `attributed_to` holds only specific refutations of the claim -- `quota-increase`: "quota increase is not the fix", "not a quota problem", "would not remove the leftover", "raising the limit would only". Each forbidden fact was probed with one sentence that asserts it while carrying hedge words ("suggest", "suspect", "rather than", "theory", "isn't"): `.scratch/probes/111-item.md`, `.scratch/probes/111-quota.md`; every probe is hit. Golden still 1.000.

## The wrong answer

`.scratch/wrong_111.md`: reads the log, takes the lease line's "cleanup reported:
successful" at face value, concludes the account hit its five-VPC ceiling and requests a
quota increase. Scores **0.3875** with golden calls (answer 0.125: only the unrefuted
forbidden fact it avoided). Golden answer scores 1.000.

## Invented

Every literal is invented for this task: job ids 3304817/3302265/3301592/3302308, GUIDs
`p7cxz`/`m2wqd`/`k5rtj`, sandbox `sandbox8842`, account 730215948861, pool
`aws-shared-pool-b`, catalog items `mesh-tracing-lab` and `fleet-hub-lab`, VPC and
endpoint ids, the variable `aws_vpc_teardown_tolerate_errors` and the role names
`aws_vpc_teardown`/`sandbox_api_lease`/`infra_aws_lab_vpc`. The incident class (dirty pooled
sandbox after a swallowed teardown failure) is invented in the mould of bench-v4's
challenge tranche; no public postmortem is its source, and nothing comes from bench-v4
or production data.
