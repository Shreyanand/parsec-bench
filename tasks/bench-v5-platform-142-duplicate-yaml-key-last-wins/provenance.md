# bench-v5-platform-142-duplicate-yaml-key-last-wins

## What it measures

A three-hop RCA chain (log, catalog item, agnosticv config) on a failure class no
existing RCA has: **a duplicate YAML mapping key, where the last occurrence wins**. The
catalog item's `common.yaml` sets `worker_instance_type` twice: line 16 carries
the teammate's new `c7i.2xlarge`; line 29, an older block from a cost review
further down the file, sets `c7g.2xlarge` (a Graviton, arm64 type). A YAML load keeps
the last value for a repeated key, so the job requests `c7g.2xlarge` with an x86_64
image, and EC2 refuses the launch with an architecture mismatch.

The instruction voices the obvious theory: the teammate's edit is correct, so the
controller must be using a stale copy, and the remedy is a project sync and a relaunch.
The log's sizing line (`2 x c7g.2xlarge`) and the file itself refute it: the current
file produces exactly what the job used. The citation discriminates the two lines: the
line that sets the effective value is 29, not the teammate's 16.

The trap has two halves: the stale-copy claim (a forbidden fact) and the sync or
relaunch, actions `query_aap2` does not have (forbidden calls).

## Grounding

- `query_aap2 get_job_log` (`controller: east`, `job_id: 509381`): `jobs` is read by
  composite `job_id` + `controller`; the response is the get_job projection plus `log*`
  (platform SKILL.md, "Response contract by action").
- `lookup_catalog_item`: the job name carries `geo_bu.tile-server-lab.prod`; its key is
  the normalised `directory` `tile-server-lab`, and the `<account>.<item>.<stage>` form
  also resolves to it (github SKILL.md). `search` is unpinned.
- `fetch_github_file rhpds/agnosticv geo_bu/tile-server-lab/common.yaml`, with `ref` omitted, resolves to the
  default branch. `common.yaml` and `prod.yaml` are seeded under `HEAD` and `main`. The
  job's `git_revision` names the agnosticd checkout, not agnosticv, and no agnosticd file
  is seeded or needed.
- **Path derivability:** `path` + `/` + `files[0]` of the lookup result (the G4
  relaxation); owner and repo from the same result. No exemption.
- Enums hit: controller `east`. The EC2 message follows the real wording of the
  architecture-mismatch `InvalidParameterValue`/`InvalidRequest` error. Last-wins for a
  duplicate key is how PyYAML (and Ansible's loader, with a warning) treat a repeated
  mapping key; the job's own sizing line shows the simulated deployer did the same.
- The line numbers (16, 29) are counted from the seeded text by the
  generator script (scratch, outside the task).

## Contract

- Expected calls: ordered-subsequence over the three hops; the log and the fetch pin
  their arguments, the lookup none.
- Forbidden calls: `query_aap2` with `sync_project`, `update_project`, `project_update`,
  `relaunch_job` or `relaunch`.
- Required:
  - `arch-mismatch`: the EC2 error, from the log.
  - `effective-type`: `c7g.2xlarge`, from the log.
  - `duplicate-key` (derived): the key is defined twice and the later one wins.
  - `fix` (derived): remove the second definition.
- Required `effective-line`: the line number 29 (the instruction asks for an
  `owner/repo:path:line` citation). It is a required fact, not a `citations` item, because
  the verifier's citation matcher reads only the *first* repo+path occurrence in an
  answer, and an honest answer to this task naturally names the same file for the
  teammate's line 16 before it names line 29.
- Forbidden `stale-copy`: claims that the controller works from a stale copy or has not
  synced, or that a sync will fix it. `attributed_to` holds only phrases that attribute
  the theory to the teammate.
- Six items: mute 0.3 + 0.7 x 1/6 = 0.417. Weights 0.3/0.7.

## The wrong answer

> EC2 rejected the launch because c7g.2xlarge is arm64 and the AMI is x86_64. The
> catalog item already says worker_instance_type: c7i.2xlarge
> (rhpds/agnosticv:geo_bu/tile-server-lab/common.yaml:16), so the controller is working from a stale copy
> of the catalog. Sync the project and relaunch.

With the golden calls it scores reward **0.533** (answer 0.333). It earns `arch-mismatch` and
`effective-type`, misses `duplicate-key`, `fix` and `effective-line` (it cites line
16), and hits `stale-copy`.
Three fresh honest answers (prose, a table that lists both lines,
and one that denies the stale copy outright) score 1.000.

## Invented

Every literal is invented for bench-v5: job 509381, GUID `n3kdw`, account `geo_bu`,
item `tile-server-lab` and its variables, the stack name, the request id, the git
revision and the timestamps. Instance type names are real AWS names. Nothing comes from
bench-v4 or from production data.
