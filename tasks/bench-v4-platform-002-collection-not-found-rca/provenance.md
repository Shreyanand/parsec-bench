# bench-v4-platform-002-collection-not-found-rca

## What it measures

The same two-service RCA chain as `-001`, on a different failure class: a missing
Ansible collection whose cause is only visible in the execution environment's
`ansible.cfg`. The log names the role; the configuration file explains why it
could not be found. Neither leg alone is a diagnosis.

## Grounding

`vendor/parsec/src/tools/aap2_fix.py`, `KNOWN_PATTERNS[3]` (list begins at
`aap2_fix.py:48`):

- its regex is `role '.*' was not found`, which the seeded log matches;
- its explanation is "Ansible collection role not found. Either the collection
  was not installed (check dynamic dependency installation in stdout) or the
  collections path is misconfigured. Verify ansible.cfg collections_path includes
  /runner/requirements_collections." The `why-missing` fact is derived from that,
  and marked `derived` with a note rather than posing as a seed literal;
- its `repo` is `_AGNOSTICD_V2_REPO` = `agnosticd/agnosticd-v2`
  (`aap2_fix.py:14`), and its `file` is `ansible.cfg` — the seeded path.

The answer shape is attested by the trajectories: one 18-call trace concluded
that a job failed because "the required Ansible collection
`agnosticd.core_workloads` was not installed in the execution environment. The
root cause is that the collection installation is commented out in the AgnosticD
configuration." The *shape* is taken from that; none of its literals are.

`dependency` is the taxonomy member for a missing collection. The operational set
(`skills/aap2-job-failure-rca/SKILL.md:90-95`) has no closer fit, and the playbook
permits the fallback list for exactly that case.

## Weighting

`0.3 / 0.7`, for the same reason as `-001`: the job id and controller are given,
the config file's owner/repo/path is not.

## Invented

Job id `90403`, the guid `kq4tn`, the log text, the `ansible.cfg` body and every
timestamp. The role name `agnosticd.core_workloads.base` extends the attested
collection name `agnosticd.core_workloads` with a plausible role. **Nothing comes
from the gitignored trace export.**
