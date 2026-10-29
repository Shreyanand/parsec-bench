# bench-v4-platform-001-ee-entrypoint-rca

## What it measures

A two-service RCA chain: read a failed job's log on `platform`, identify the
execution-environment invocation bug it reveals, then read the file in the
AgnosticD content repository on `github` that has to change — and produce the
citation and the single taxonomy category parsec's own RCA playbook requires.

This is the shape-A exemplar. Nine scenarios follow it.

## Grounding

`vendor/parsec/src/tools/aap2_fix.py` at the pinned commit `28e2c40`,
`KNOWN_PATTERNS[1]` (the list begins at `aap2_fix.py:48`):

- its regex is `unrecognized arguments:.*--private-data-dir`, and the seeded log
  contains that string, so the seed is a case the real fix engine would match;
- its explanation is "EE entrypoint bug — the chained entrypoint does not detect
  AAP container group mode (ansible-runner worker). It falls into the wrong code
  path and passes runner args to ansible-playbook. Fix: detect
  KUBERNETES_SERVICE_HOST env var in entrypoint.sh and install the
  ansible-playbook wrapper." That is what the `invocation-meaning` required fact
  is derived from, which is why it is marked `derived` with a note rather than
  pretending to be a seed literal;
- its `repo` is `_AGNOSTICD_V2_REPO`, defined at `aap2_fix.py:14` as
  `agnosticd/agnosticd-v2` — the owner half that 21 real trajectory calls got
  wrong as `rhpds/agnosticd-v2`, and the reason the forbidden call list names
  that pair for both github tools;
- its `file` is `tools/execution_environments/ee-multicloud-public/entrypoint.sh`,
  which is the seeded file's path. `ee-multicloud-public` also occurs at
  `aap2_debug.py:181-182`.

The category taxonomy and the `high`/`medium`/`low` confidence come from
`vendor/parsec/skills/aap2-job-failure-rca/SKILL.md:90-95`. `automation_failure`
is the operational-set member that fits an execution-environment invocation bug;
`platform_failure` and `connectivity_failure` do not, and the verdict matcher's
`exclusive` default means naming a second category fails the fact.

The template name `RHPDS sandboxes-gpte.ans-bu-wksp-rhel-90.prod-zhkrm-provision`
occurs verbatim at `vendor/parsec/docs/ARCHITECTURE.md:194`, satisfying the
identifier rule outright.

## Weighting

`0.3 / 0.7`. The job id and controller are handed over by the instruction, so the
first call is close to free. The second call is not: its owner, repo and path
have to be derived from the log's error and the pattern it matches, and getting
the owner wrong is the single most common real mistake. That is worth more than
the `0.2` an entirely-given-id scenario gets, and less than the `0.5` a genuine
two-hop discovery chain earns.

Measured 2026-09-07: golden `1.000`, floors mute `0.440`, no-call `0.140`,
fabricate `0.300`. The fabricate floor sits below the mute floor, which is the
check that matters: asserting one of the four other `KNOWN_PATTERNS` signatures
scores worse than saying nothing.

## Invented

Job id `90402` (in the reserved 90000–99999 range), the log text, the
`entrypoint.sh` body, the `guid` `zhkrm` as it appears in a job record, and every
timestamp. **Nothing here comes from the gitignored trace export.**

The seed carries all 23 platform collections and all 5 github collections, the
unused ones as empty lists, because the generated `schema.json` sets
`additionalProperties: false` and the installer requires the collection set to
match.
