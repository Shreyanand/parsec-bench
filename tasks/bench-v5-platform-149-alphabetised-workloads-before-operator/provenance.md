# bench-v5-platform-149-alphabetised-workloads-before-operator

## What it measures

A five-call RCA (log, catalog item, agnosticv config, agnosticv PRs, the failing role)
on a failure class no existing task has: **a cosmetic change that broke an execution
order dependency**. A merged agnosticv PR (#31588, "Sort workload lists alphabetically
... (no functional change)") sorted the item's `workloads` list. agnosticd runs
workloads in list order, so `ocp4_workload_kafka_topics` now runs before
`ocp4_workload_streams_operator`, the workload that installs the Strimzi CRDs. The
topics step fails with `Failed to find exact match for
kafka.strimzi.io/v1beta2.KafkaTopic`, and the operator never runs.

The instruction voices the obvious reading of a missing kind: the latest Strimzi
release dropped `v1beta2`, so pin the operator. The agent must see that the operator
never ran in this job (it is absent from the log), find it last in the item's list,
read the role's stated dependency, and find the PR that reordered the list. That PR is
`closed` (merged), so the default open-only PR search returns only the decoy: an open,
unmerged Kafka-version PR on the same file.

## Tranche

**Challenge.** Expected to score below 1.0 for a good agent. The agent failure it
exposes is **trusting a change's self-description and reading a missing resource as
an upstream removal**: the PR title says "no functional change", the error names an
API version, and the first PR the agent finds touches the right file but was never
merged. Only an agent that reasons about run order from the list and the role, and
searches closed PRs, reaches the cause.

## Grounding

- `query_aap2 get_job_log`: composite `job_id` + `controller` on `jobs`; the row carries
  `git_url` / `git_revision`, so the agnosticd fetch's repository comes from the result
  and its path from the log's `task path:` line. Controller `event0` is an api.json enum
  value.
- `lookup_catalog_item`: the stored row's lookup key is `directory`
  `payments-eventbus-lab`; `path` + `files[0]` gives the expected agnosticv path. Both
  item files are seeded under `HEAD` and `main`.
- `search_agnosticv_prs` (github SKILL.md): the effective state is `open` when omitted,
  so only #31602 is returned; with `state: all` (or `closed`) #31588 is returned too. A
  keyword matching a title returns all its files; one matching only a file path returns
  just the matching paths (the golden's #31588 entry, searched by item name, lists only
  this item's `common.yaml`). Results keep stored order. The expected call pins no
  argument: `search` is free text and `state` is the agent's to choose (hazard 19).
- `fetch_github_file` for the role: seeded under `HEAD`, `main` and the job's
  `git_revision`.

## Contract

Weights 0.25 / 0.75 (five calls), `unordered-subset`: the agnosticv branch (lookup,
config, PRs) and the agnosticd branch (role file) are siblings, and each pinned path
already forces its own dependency.

- `operator-workload`: `ocp4_workload_streams_operator`, never in the log.
- `pr`: `31588`, only from a closed-PR search.
- `sorted`: what the PR changed (the list order).
- `ran-before-operator` (derived): the run-order mechanism.
- `fix-order` (derived): restore the operator ahead of the topics workload.
- forbidden `api-removed` (with `attributed_to` only for sentences naming the event
  lead's theory) and `kafka-bump`, written as claims (hazard 22).

Mute answer floor: 2 forbidden of 7 answer items, reward 0.464.

## The wrong answer

`/tmp/ext/scratch/bench-v5-platform-149-alphabetised-workloads-before-operator/wrong.md`: reads the log, takes the missing kind as an API
removal, finds the open Kafka PR with the default search, and backs pinning the
operator. With the golden calls it scores **0.357** (it earns only `operator-workload`, from
quoting the channel setting); a second phrasing (`wrong2.md`) also scores 0.357. Golden
1.000.

Honest panel, all **1.000**: two authored answers (`honest1-2.md`: prose, and `Key: value`
bullets that deny the API-removal theory) and three blind answers by a separate agent from
the instruction and the tool results only (`blind-a/b/c.md`). The two authored answers first
scored 0.893 ("hadn't been installed", "is listed before"), so `ran-before-operator` and
`fix-order` were widened.

## Invented

Every literal is invented: job 9917306, GUID `w5jhb`, the catalog item
`finserv_bu/payments-eventbus-lab` and its siblings named in the PR, PRs #31588 and
#31602 with their authors and branches, the roles `ocp4_workload_kafka_topics`,
`ocp4_workload_streams_operator` and `ocp4_workload_payments_app` and their variables,
the topic names, the revision and every timestamp and figure. The incident class (a
"no functional change" reorder that breaks an install-order dependency) is invented in
the mould of bench-v4's challenge tranche; no public postmortem is its source, and
nothing comes from bench-v4 or production data.
