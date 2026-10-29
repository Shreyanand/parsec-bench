## What it measures

An upgrade that silently drops a catalog override. The catalog item sets
`ocp4_workload_netbox_ipam_db_storage_gi: 60` and deploys agnosticd-v2 at `scm_ref: v2.12.0`.
In that release the role renamed the variable. Its defaults say
`ocp4_workload_netbox_ipam_db_storage_gi` "is removed and no longer read" and define
`ocp4_workload_netbox_ipam_db_storage_size: 10Gi` (line 13), now a Kubernetes quantity.
Ansible does not complain about an extra variable nobody reads, so the 60 GiB request is
dropped and orders get 10Gi, which is less than the ~45 GiB attendees import.

The chain is two fetches: the catalog item (whose `scm_ref` gives the release), then the
role's defaults at that ref. The answer needs the release, the effective size, the reason
the override is dead, the deciding line, and the exact replacement (`..._db_storage_size:
60Gi`: new name and quantity form).

**Kind: trap.** The catalog "already asks for 60 GiB", so the natural reading is that the
setting applies and the cause is elsewhere, or that the number should be raised.

## Grounding

- github SKILL.md "/fetch_github_file": `files` by owner, repo, path and effective `ref`
  (the request `ref` when given, otherwise the default branch). Success is exactly
  `{content}`.
- Seed: `files` 6. The catalog item under `HEAD` and `main`. The role's defaults under
  `v2.12.0`, `main` and `HEAD` (identical: nothing changed since the tag), and under
  `v2.11.0` (the old release, with `..._db_storage_gi: 30`) for an agent that compares.
- Derivability: `ref: v2.12.0` and the owner/repo `agnosticd`/`agnosticd-v2` appear in the
  first call's result (`scm_url`, `scm_ref`); both paths are in the instruction.

## Contract

- tool_calls (0.3), ordered-subsequence (the ref comes from the first result): the catalog
  fetch {rhpds, agnosticv, path}, then the role fetch {agnosticd, agnosticd-v2, path,
  ref: v2.12.0}. Forbidden: any `fetch_github_file` from `rhpds/agnosticd-v2` (the classic
  wrong owner) or from `agnosticd/agnosticd` (the legacy repository).
- answer (0.7), `fold_markup` on: required `release` (v2.12.0), `size` (10Gi), `new-name`,
  `ignored` (derived), `line` (13, derived) and `fix` (derived: `..._db_storage_size: 60Gi`).
  Citation `role-defaults` (agnosticd/agnosticd-v2 + path; no line, because the file is named
  more than once in an honest answer and the matcher reads the first mention). Forbidden
  `override-applies` (claims that orders get 60 GiB) and `raise-old-name` (raising the dead
  variable).
- Items: 9. Mute 0.3 + 0.7 x 2/9 = 0.456.

## The wrong answer

"The item deploys v2.12.0, and the catalog sets ocp4_workload_netbox_ipam_db_storage_gi: 60,
so new orders get 60 GiB. Attendees simply import more than that: raise
ocp4_workload_netbox_ipam_db_storage_gi to 100." With the golden calls it scores reward **0.456** (answer 0.222: `release` and the citation only; both forbidden facts hit), equal to the mute floor. Three fresh honest answers (terse prose, a table that answers "honoured? No", and one that mentions the old release first) score 1.000.

## Invented

Every literal is invented: the catalog item and its account directory, the role, its
versions and sizes, the release tags `v2.11.0` and `v2.12.0`, and the date. `rhpds/agnosticv`,
`agnosticd/agnosticd-v2` and `agnosticd/agnosticd` are the real repository names shared by
both splits. Nothing comes from bench-v4 or from production data.
