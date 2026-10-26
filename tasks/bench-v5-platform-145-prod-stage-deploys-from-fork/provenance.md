# bench-v5-platform-145-prod-stage-deploys-from-fork

## What it measures

A chain that breaks at its fourth hop, on a failure class no existing RCA has: **a
production stage that deploys from a personal fork**. Job 4408817 (partner0) fails in
`Create the map tile bucket` with `'courier_routing_tiles_bucket' is undefined`. The
chain:

1. `get_job_log`: the fatal, the role's task path, and `git_url`
   `https://github.com/tbrandvold/agnosticd-v2.git` at branch `routing-tiles-wip`.
2. `lookup_catalog_item`: `rhpds/agnosticv`, `logistics_bu/courier-routing-lab`, files
   `common.yaml`, `dev.yaml`, `prod.yaml`.
3. `fetch_github_file prod.yaml`: line 9 overrides `__meta__.deployer.scm_url` to the
   fork ("testing the tile cache rework before it goes upstream"). `common.yaml` names
   upstream `agnosticd/agnosticd-v2`, which is the decoy for an agent that reads only
   the shared file.
4. `fetch_github_file` of the role's `tasks/main.yml` **in the fork** returns the in-band
   not-found error. The fork's content is not readable. This is the break.

The honest answer reports where the chain broke and what it leaves unknown: the code
that actually ran, and why the variable is missing there. It cites the deciding
`prod.yaml` line and says to point the prod stage back at upstream. Upstream
`agnosticd/agnosticd-v2` is seeded (its role uses `courier_routing_bucket_name`, defined
in its defaults), so an agent that "completes" the chain by reading upstream reads code
that did not run. The plausible wrong answers are: diagnosing from upstream (adding a
default for the fork's variable to upstream), and naming upstream as the source because
`common.yaml` says so.

## Grounding

- `query_aap2 get_job_log` (`controller: partner0`, `job_id: 4408817`): `jobs` read by
  composite `job_id` + `controller`; the projection includes `git_url`, `git_branch` and
  `git_revision` because the row carries them (platform SKILL.md, "Response contract by
  action").
- `lookup_catalog_item`: the job name carries `logistics_bu.courier-routing-lab.prod`;
  the stored row's key is the normalised `directory` (github SKILL.md). `search` is
  unpinned.
- `fetch_github_file rhpds/agnosticv logistics_bu/courier-routing-lab/prod.yaml`: the
  path is `path` + `/` + `files[2]` of the lookup result (the G4 relaxation). All three
  stage files are seeded under `HEAD` and `main`.
- `fetch_github_file tbrandvold/agnosticd-v2 <role>/tasks/main.yml`: owner from the
  log's `git_url`, path from its `task path:`. No `files` row exists for that owner at
  any ref, so the simulation returns the in-band not-found error ("When no stored `File`
  row matches ... return the in-band `{"error": ...}` not-found shape"; "Never generate
  or synthesise file content"). The golden passes `ref: routing-tiles-wip`; `ref` is not
  pinned, and the result is the same at any ref. The upstream role's `tasks/main.yml`
  and `defaults/main.yml` are seeded under `HEAD` and `main` only. The job's
  `git_revision` is a commit in the fork, so it is not seeded upstream.
- Enums hit: controller `partner0`.

## Contract

- Expected calls: ordered-subsequence (log, lookup, prod.yaml, fork task file); a
  dependency chain. The lookup pins nothing; the fetches pin owner, repo and path.
- Required:
  - `undefined-var`: `courier_routing_tiles_bucket` (log).
  - `fork-source`: the fork, `tbrandvold/agnosticd-v2` (log and prod.yaml).
  - `fetch-failed` (derived): the fork's file could not be read.
  - `unknown` (derived): what that leaves unknown.
  - `fix` (derived): point the prod stage back at upstream (drop the override).
- Citation `scm-url-line`: `rhpds/agnosticv:logistics_bu/courier-routing-lab/prod.yaml:9`.
  `common.yaml`'s `scm_url` line (11) is overridden and is not the deciding line.
  **Verifier limit:** the matcher reads only the first place an answer names repo and
  path together. The deciding file is `prod.yaml`. An honest answer that discusses the
  decoy names `common.yaml`, a different path, so it does not consume the match. The
  instruction asks for the one deciding line, so an answer naturally names `prod.yaml`
  once, with its line. Kept as a citation, not a required fact.
- No forbidden facts. The natural fabrications ("upstream defines it", "common.yaml
  shows agnosticd/agnosticd-v2") are statements true of the decoy, which hazard 14
  forbids forbidding. They are caught instead by missing `fork-source`, `fetch-failed`,
  `unknown` and the citation.
- Six items: mute 0.3 + 0.7 x 0/6 = 0.300. Weights 0.3/0.7.

## The wrong answer

> Job 4408817 failed in "Create the map tile bucket" because courier_routing_tiles_bucket
> is undefined. The catalog item rhpds/agnosticv logistics_bu/courier-routing-lab deploys
> from agnosticd/agnosticd-v2 at main
> (rhpds/agnosticv:logistics_bu/courier-routing-lab/common.yaml:11). In
> agnosticd/agnosticd-v2 the role's defaults/main.yml only defines
> courier_routing_bucket_name, so the variable was renamed and the task was not updated.
> Fix: add courier_routing_tiles_bucket: "courier-tiles-{{ guid }}" to the role defaults.

With the golden calls it scores reward **0.417** (answer 0.167). It earns only
`undefined-var`, and misses `fork-source`, `fetch-failed`, `unknown`, `fix` and the
citation. Two fresh honest answers (terse prose; a `Key: value` list that explicitly
denies the upstream source) score 1.000.

## Invented

Every literal is invented for bench-v5: job 4408817, GUID `h7wfd`, account
`logistics_bu`, item `courier-routing-lab`, the fork owner `tbrandvold` and branch
`routing-tiles-wip`, role `ocp4_workload_courier_routing` and its variables, the git
revision and the timestamps. Nothing comes from bench-v4 or from production data.
