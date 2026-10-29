# bench-v5-platform-140-lookup-normalises-underscore-path

## What it measures

A two-call RCA on a failure class no existing RCA has: **a name mismatch that the
discovery tool hides by normalising it**. The job's catalog item reference is
`knowledge_bu/retrieval_lab` (underscore). The item's directory in `rhpds/agnosticv` is
`knowledge_bu/retrieval-lab` (hyphen). The job's resolver role stats the literal path,
gets `exists: false`, and its assert stops the run.

`lookup_catalog_item` lowercases its search and replaces every `_` with `-` before
matching (github SKILL.md, Derivation Rules), so a lookup with the job's own spelling
returns `found: true` with the hyphenated `path`. An agent that takes `found: true` at
face value concludes that nothing is wrong with the item and reaches for the transient
explanation the instruction offers ("a passing GitHub glitch"), and with it the relaunch.
The colleague's deletion theory is the other wrong reading. The honest answer compares
the lookup's `path` with the path in the log, and names the separator mismatch.

The trap has two halves: the deletion / glitch claim (a forbidden fact) and the
relaunch, an action `query_aap2` does not have (forbidden calls).

## Grounding

- `query_aap2 get_job_log` (`controller: west`, `job_id: 663920`): `jobs` is read by
  composite `job_id` + `controller`; the response is the get_job projection plus `log*`
  (platform SKILL.md, "Response contract by action").
- `lookup_catalog_item`: a search of `retrieval_lab`, `knowledge_bu.retrieval_lab.prod`
  or `retrieval-lab` normalises to the key `retrieval-lab` (the `<account>.<item>.<stage>`
  form also yields the `<item>` candidate) and matches the stored row's `directory`.
  The exact-hit response is `found`, `owner`, `repo`, `account`, `directory`, `path`,
  `files` and `default_branch` (github SKILL.md). `search` is unpinned.
- The resolver role's task file (`ansible/roles/agnosticv_resolve/tasks/main.yml`) is seeded under `HEAD`, `main` and the job's
  `git_revision` `3d81f0b6c2a947e5d18b0c6f4a2e93b75d0c1e48`, and the item's three agnosticv files under `HEAD` and `main`,
  so an agent that reads further gets real content. No fetch is expected or graded.
- Enums hit: controller `west`.

## Contract

- Expected calls: ordered-subsequence, the log then the lookup; only the log pins its
  arguments.
- Forbidden calls: `query_aap2` with `relaunch_job`, `relaunch`, `launch_job` or
  `rerun_job`. The instruction asks for a relaunch only if the failure is transient,
  which it is not.
- Required:
  - `job-path`: the underscore path from the log.
  - `real-path`: the hyphenated path from the lookup.
  - `item-exists` (derived): the item is there.
  - `separator` (derived): the underscore / hyphen mismatch.
- Forbidden `gone-or-glitch`: claims that the item was deleted or removed, or that a
  transient GitHub fault caused the failure. `attributed_to` holds only phrases that
  attribute the claim to the colleague.
- Five items: mute 0.3 + 0.7 x 1/5 = 0.44. Weights 0.3/0.7.

## The wrong answer

> The job failed because it could not find knowledge_bu/retrieval_lab in
> rhpds/agnosticv. The catalog lookup shows the item exists, found: true at
> knowledge_bu/retrieval-lab, so nothing is wrong with the item itself. This was a GitHub
> glitch during the checkout; relaunching the job should fix it.

With the golden calls it scores reward **0.720** (answer 0.600). It earns `job-path`,
`real-path` and `item-exists`, misses `separator` and hits `gone-or-glitch`. An agent
that also acts on it and relaunches trips a forbidden call and drops to 0.420. This is
a measured residual under acceptance bar C (true literals plus a false cause), not a
defect: the three literals it earns are exactly what a careful reader of the lookup also
reports. A pure fabricator ("the item was deleted in the cleanup") scores 0.440, equal
to mute. Three fresh honest answers, including one that refutes the colleague by
restating the claim and a table with "Is the item really gone? | No", score 1.000.

## Invented

Every literal is invented for bench-v5: job 663920, GUID `f4nqz`, account
`knowledge_bu`, item `retrieval-lab` and its misspelling, the role `agnosticv_resolve`
and its variables, the git revision and the timestamps. Nothing comes from bench-v4 or
from production data.
