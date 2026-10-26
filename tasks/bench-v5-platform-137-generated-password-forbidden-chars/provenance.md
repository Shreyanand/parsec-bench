# bench-v5-platform-137-generated-password-forbidden-chars

## What it measures

A two-hop RCA on a failure class no existing RCA has: an **intermittent failure caused
by a randomly generated value**. The role generates the RDS admin password on every
run with `lookup('ansible.builtin.password', '/dev/null', length=16,
chars=['ascii_letters', 'digits', 'punctuation'])`. Python's `string.punctuation`
contains `/`, `@` and `"`, which RDS refuses in `MasterUserPassword`. A run fails only
when its 16 random characters include one of them. So identical code succeeds on some
orders and fails on others, which is what the user reports.

The log gives the AWS error, but the password task runs with `no_log: true`, so its
output is censored. Only the task file shows that the value is random per run
(`/dev/null` as the lookup's file means nothing is persisted), and that its character
set includes punctuation. The answer joins three things: the intermittency, the
character set and the AWS rule. The fix is in the generator, not a retry.

## Grounding

- `query_aap2 get_job_log` (`controller: west`, `job_id: 694251`): `jobs` is read by
  composite `job_id` + `controller`. The response is the get_job projection plus `log*`
  (platform SKILL.md, "Response contract by action"). The row carries the git fields.
- `fetch_github_file agnosticd/agnosticd-v2 ansible/roles/claims_warehouse_rds/tasks/main.yml`,
  with `ref` omitted, resolves to the default branch. The task file and the role's
  `defaults/main.yml` are seeded under `HEAD`, `main` and the job's `git_revision`
  `e3a91c07b5d24f68a0c2e7d19b4f3a6c85d0e2f1`, with identical content.
- **Path derivability:** the path is a substring of the log's `task path:` lines. Owner
  and repo come from `git_url`. No exemption is needed.
- The AWS message is RDS's real wording for this rejection. The failure probability
  (about 40% per run: 1 - (91/94)^16) is not graded and not stated in the instruction.
- Enums hit: controller `west`.

## Contract

- Expected calls: ordered-subsequence, log then task file. No forbidden calls, no
  citation.
- Required:
  - `password-rejected`: the rejected parameter, from the log.
  - `password-source`: the variable or the lookup that makes it, from the file.
  - `random-per-run`: derived. The value is regenerated on each run.
  - `punctuation-chars`: derived. The character set includes the characters RDS forbids.
  - `charset-fix`: derived. Narrow the character set.
- Forbidden fact `wrong-cause`: a transient AWS/RDS problem, or a length/complexity
  problem. No `attributed_to`.
- Six items: mute 0.3 + 0.7 x 1/6 = 0.417. Weights 0.3/0.7.

## The wrong answer

> RDS returned InvalidParameterValue for the master password on CreateDBInstance. The
> other orders worked on the same code, so this was a transient RDS outage in that
> region; just rerun the order and it should go through.

With the golden calls it scores reward **0.417** (answer 0.167). It gets
`password-rejected`, misses the other four required facts and hits `wrong-cause`.

## Invented

Every literal is invented for bench-v5: job 694251, GUID `vt3kc`, account `insurance_bu`,
item `claims-analytics-lab`, the role `claims_warehouse_rds` and its variables, the DB
identifier, the request id, the git revision and the timestamps. Nothing comes from
bench-v4 or from production data.
