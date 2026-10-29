# bench-v5-platform-107-host-pattern-skipped-play

## What it measures

The fatal is an undefined hostvar (`bastion_ssh_key`), and a colleague wants to paper
over it with a fallback value. The cause is earlier in the log: `[WARNING]: Could not
match supplied host pattern, ignoring: bastions`, then `skipping: no hosts matched` for
the play whose `set_fact` publishes the key. The play targets `hosts: bastions`, but the
inventory group (shown by both the add_host output and the group-listing debug) is
`bastion`. The agent must:

- treat the warning, not the fatal, as the cause;
- read the playbook to find the pattern;
- cite the line to change.

## Grounding

- `query_aap2 get_job_log` (`east`, `372861`): composite `jobs` read.
- `fetch_github_file agnosticd/agnosticd-v2 ansible/configs/quantum-sim-lab/pre_software.yml`,
  `ref` omitted. Seeded under `HEAD` and `main`. The path is in the log's `task path:`
  lines, and `git_url` names the repo.
- The `task path:` line numbers in the log (7 and 30) are the real `- name:` lines of the
  seeded playbook. `gen_107.py` computes them with `line_of`.

## Contract

- Expected calls: ordered-subsequence, log then playbook. Weights 0.3/0.7. No forbidden
  calls.
- Required: `pattern-warning` is the log literal. `play-skipped` (derived) and
  `group-name` (derived) state the pattern-vs-group mismatch.
- Citation: line 12, `hosts: bastions`, counted from the seeded text.
- Forbidden fact `default-fix`: "add a default", "| default", "default(" and the like.
  No `attributed_to`; the golden answer argues against the fallback without those forms.

## The wrong answer

> bastion_ssh_key is undefined in "Write the key into the lab user secret" ... add a
> default, e.g. `| default('')`.

`score.py --golden-calls` gives **0.30** (answer 0.0). It misses all three required
facts and the citation (no line), and hits `default-fix`.

## Invented

Every literal is invented for bench-v5: job 372861, GUID `q2lmz`, the config
`quantum-sim-lab` and its playbook, the bastion hostname, the group `simulators` and the
git revision.
