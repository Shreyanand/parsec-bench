# bench-v5-platform-136-provision-key-mode-too-open

## What it measures

A two-hop RCA on a failure class no existing RCA has: a file-permission defect. The
role that writes the run's SSH private key into the execution environment gives it
mode `"0644"`. OpenSSH refuses to use a private key that is readable by group or
others, so it ignores the key and never offers it. The bastion then answers
`Permission denied (publickey,...)`, and Gathering Facts on the bastion goes
UNREACHABLE.

The last line of the log reads like an authorization failure on the bastion, and the
instruction voices the obvious remedy (rotate the EC2 key pair). The cause is in the
earlier lines of the same UNREACHABLE message (`WARNING: UNPROTECTED PRIVATE KEY
FILE!`, `Permissions 0644 ... are too open`, `bad permissions`). The fix belongs in the
task that wrote the file. The key-writing task runs with `no_log: true`, so its log
output is censored. Only the task file shows where the mode is set, and the citation
line (15) is not the task's `task path:` line (10).

## Grounding

- `query_aap2 get_job_log` (`controller: east`, `job_id: 552816`): `jobs` is read by
  composite `job_id` + `controller`. The response is the get_job projection plus
  `log*` (platform SKILL.md, "Response contract by action"). The row carries
  `git_url`, `git_branch` and `git_revision`, so they are returned.
- `fetch_github_file agnosticd/agnosticd-v2 ansible/roles/bastion_provision_key/tasks/main.yml`,
  with `ref` omitted, resolves to the default branch (github SKILL.md). The file and the
  role's `defaults/main.yml` are seeded under `HEAD`, `main` and the job's
  `git_revision` `5be08d3f71a2c94e60d1b7a83f2c5e19d04a6b7e`, with identical content.
- **Path derivability:** the path is a substring of the log's `task path:` lines
  (`/runner/project/ansible/roles/bastion_provision_key/tasks/main.yml:10`). Owner and
  repo come from the result's `git_url`. No exemption is needed.
- Enums hit: controller `east`. The ssh message text follows OpenSSH's real wording.
- `gen136.py` (scratch, outside the task) counts the citation line from the seeded text.

## Contract

- Expected calls: ordered-subsequence, log then task file. Only the fetch pins owner,
  repo and path. No forbidden calls.
- Required:
  - `key-too-open`: the permission complaint, from the log.
  - `writing-task`: the task or role that wrote the key, from the log.
  - `fix-mode`: derived. An owner-only mode (`0600`/`0400`) in that task.
- Citation `mode-line`: `agnosticd/agnosticd-v2:ansible/roles/bastion_provision_key/tasks/main.yml:15`.
- Forbidden fact `bastion-rejected-key`: claims that the bastion rejected the key, that
  the key is missing from `authorized_keys`, or that the key pair is wrong. No
  `attributed_to`. The forms are claims, so a denial ("not a wrong key pair") is
  excused by the polarity reading.
- Five items: mute 0.3 + 0.7 x 1/5 = 0.44. Weights 0.3/0.7.

## The wrong answer

> The bastion rejected the key: ssh got `Permission denied (publickey)` from
> bastion.qz7hd.fieldops.example, so the key pair registered in EC2 for qz7hd does not
> match the key the job used. It's a wrong key pair; rotate the EC2 key pair and re-run.

With the golden calls it scores reward **0.300** (answer 0.000). It misses all three
required facts and the citation, and hits `bastion-rejected-key`.

## Invented

Every literal is invented for bench-v5: job 552816, GUID `qz7hd`, account `fieldops_bu`,
item `sensor-gateway-workshop`, the role `bastion_provision_key` and its variables, the
host name, the git revision and the timestamps. `198.51.100.47` is a TEST-NET-2
documentation address. Nothing comes from bench-v4 or from production data.
