# bench-v5-platform-138-project-prefix-not-a-dns-label

## What it measures

A three-hop RCA chain (log, catalog item, agnosticv config) on a failure class no
existing RCA has: a **Kubernetes object-name syntax violation**. The workload role
names each team project `"{{ team_projects_prefix }}-{{ guid }}-team{{ item }}"`. The
catalog item's `common.yaml` sets `team_projects_prefix: Tidewater_Ops`. The rendered
names (`Tidewater_Ops-m2wjr-team1` .. `team4`) contain uppercase letters and an
underscore. OpenShift rejects each one with 422 `Invalid value ... a lowercase RFC 1123
label must consist of lower case alphanumeric characters or '-'`.

The log gives the refused name and the rule, but not the variable. The role default
(`team_projects_prefix: bootcamp`) is valid, and it is seeded as the wrong-file decoy:
only the catalog item's override explains the bad value. So the citation proves that
the agnosticv file was read. The fix is a value: a lowercase, hyphenated prefix.

## Grounding

- `query_aap2 get_job_log` (`controller: event0`, `job_id: 731608`): `jobs` is read by
  composite `job_id` + `controller` (platform SKILL.md). The row carries the git fields.
- `lookup_catalog_item`: the job name carries `summit_bu.coastal-sre-bootcamp.prod`. Its
  exact key is the normalised `directory` `coastal-sre-bootcamp`, and the
  `<account>.<item>.<stage>` form also resolves to it (github SKILL.md). `search` is
  unpinned.
- `fetch_github_file rhpds/agnosticv summit_bu/coastal-sre-bootcamp/common.yaml`, `ref`
  omitted, resolves to the default branch. The agnosticv files are seeded under `HEAD`
  and `main`. The role's `tasks/workload.yml` and `defaults/main.yml` in
  `agnosticd/agnosticd-v2` are seeded under `HEAD`, `main` and the job's `git_revision`
  `7d40b2e9c18f5a63e0b9d42c1f7a8e35b6c09d14`.
- **Path derivability:** the fetched path is lookup's `path` + `/` + `files[0]`, which is
  the one-dict join the gate accepts. No exemption is needed.
- The 422 Status body follows the Kubernetes API's real wording for an invalid
  namespace name. Enums hit: controller `event0`.
- `gen138.py` (scratch, outside the task) counts the citation line (18) from the seeded
  text.

## Contract

- Expected calls: ordered-subsequence over the three hops. Only the fetch pins owner,
  repo and path. No forbidden calls.
- Required:
  - `refused-name`: the namespace name from the log.
  - `label-rule`: the RFC 1123 rule or the offending characters.
  - `prefix-var`: `team_projects_prefix`, named only in the github files.
  - `fix-value`: derived. A lowercase hyphenated value, such as `tidewater-ops`.
- Citation `prefix-line`: `rhpds/agnosticv:summit_bu/coastal-sre-bootcamp/common.yaml:18`.
- Forbidden fact `wrong-cause`: claims that the name is too long, that the namespace
  already existed, or that permissions are missing. No `attributed_to`. None of the
  forms is a seed literal.
- Six items: mute 0.3 + 0.7 x 1/6 = 0.417. Weights 0.3/0.7.

## The wrong answer

> The project Tidewater_Ops-m2wjr-team1 was refused with 422 Invalid value on
> metadata.name: the name is too long for a namespace once the GUID and team suffix are
> added. Shorten the prefix in the role defaults.

With the golden calls it scores reward **0.417** (answer 0.167). It gets `refused-name`,
misses `label-rule`, `prefix-var`, `fix-value` and the citation, and hits `wrong-cause`.

## Invented

Every literal is invented for bench-v5: job 731608, GUID `m2wjr`, account `summit_bu`,
item `coastal-sre-bootcamp`, the prefix `Tidewater_Ops`, the role
`ocp4_workload_team_projects` and its variables, the git revision and the timestamps.
Nothing comes from bench-v4 or from production data.
