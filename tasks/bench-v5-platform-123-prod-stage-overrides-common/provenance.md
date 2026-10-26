# bench-v5-platform-123-prod-stage-overrides-common

## What it measures

agnosticv stage layering. The catalog item `openshift-ai-pipelines-workshop` (rhpds/agnosticv,
`ai_bu`) has a shared `common.yaml` and stage files `dev.yaml` and `prod.yaml`. The prod stage
is `common.yaml` with `prod.yaml` merged on top:
- The OpenShift version (`"4.17"`) is set **only** in common.yaml.
- Worker count, worker type and `num_users` are set in common.yaml (2 × m6i.2xlarge, 10
  users) and **overridden** in prod.yaml (5 × m6i.4xlarge, 40 users).
- dev.yaml sets 4.18, which is a decoy for anyone who reads every stage file as one.

A correct answer needs both files and the precedence rule, plus a citation of prod.yaml's
worker-count line. The lookup's `path` points at prod.yaml (the suite's convention), so an
agent that reads only that file cannot give the version, and one that reads only common.yaml
gives the wrong sizing.

**Kind: happy.** All three calls succeed. The difficulty is the synthesis.

## Grounding

- github SKILL.md "/lookup_catalog_item": an exact hit on normalised `directory` returns
  `found: true` with `owner`, `repo`, `account`, `directory`, `path`, `files` and
  `default_branch`.
- "/fetch_github_file": exact (owner, repo, path, effective ref). All three stage files are
  seeded under HEAD and main.
- Seed: `catalog_items` 1, `files` 6 (common, prod, dev × HEAD/main).
- leakage.py WARN: weak literals (`worker_instance_count`, `worker_instance_type`,
  `openshift-workloads`, `description.adoc`, `cloud_provider`) are agnosticv vocabulary shared
  by design.

## Contract

- tool_calls (0.3), unordered-subset: the lookup {search: openshift-ai-pipelines-workshop}
  and both fetches (common.yaml and prod.yaml are siblings in any order).
- answer (0.7): required `ocp-version` (4.17), `worker-type` (m6i.4xlarge), `prod-wins`
  (derived). Counts workers = 5 and attendees = 40. Citation rhpds/agnosticv prod.yaml line 13.
  Forbidden `common-as-prod` ("2 workers", "10 attendees", ...), excused only by phrases that
  put the value in its place ("common.yaml's", "only the default", "overrides common",
  "default for stages"). Forbidden `dev-version` (4.18 as the prod version).
- Probe: "Prod builds 2 workers, not more, and is sized for 10 attendees rather than 40." hits
  `common-as-prod`. "not" and "rather than" excuse nothing.

## The wrong answer

The common.yaml-only reading ("...installs OpenShift 4.17 with 2 workers of type m6i.2xlarge,
sized for 10 attendees...") scores reward **0.475** with the golden calls (0.3 of it is the
tool component). The answer component is 0.25: only the version survives. The golden answer
scores 1.0. Mute floor (validate.py): answer 0.25, reward 0.47 with golden calls.

## Invented

Every literal is invented: the item, the `ai_bu` account, the stage files' content, the
scm_ref and the sizes. Nothing comes from bench-v4 or from production data.

## Gate exemptions

- expected-call-underivable: fetch_github_file.path=ai_bu/openshift-ai-pipelines-workshop/common.yaml — sibling of `prod.yaml` in the same agnosticv item directory: the `lookup_catalog_item` result gives `path` `ai_bu/openshift-ai-pipelines-workshop/prod.yaml` and lists `common.yaml` in `files`, so replacing the file name in that `path` gives the value; the fetched `prod.yaml` also opens with "overrides common.yaml". The G4 join (`A + "/" + B` from one dict) cannot see it because the result's `directory` omits the account `ai_bu` and its `path` names a file, not the directory (owner-approved 2026-10-13, `owner-decisions.md` 2b).
