# bench-v5-platform-104-cfn-dependency-and-what-changed

## What it measures

Two questions about one failed provision, each answered by a different source.

- **Why it failed:** CloudFormation `Template format error: Unresolved resource
  dependencies [PublicSubnetB]`. The cause is only visible in the rendered template's
  Jinja source. `PublicSubnetB` is inside `{% if subnet_count | int > 1 %}`, but its
  route-table association, which `!Ref`s it, is outside the guard. The log shows
  `subnet_count=1`.
- **What it already changed:** the log is trimmed (the controller kept 1873 of 2214660
  bytes), so the two AWS-side changes made early in the run (an EC2 key pair and an S3
  bucket) are only in `job_events`. The first expected use of `changed_only: true` in
  the suite fetches them.

The wrong answer lists stack resources (a VPC) for cleanup, although the stack failed
validation and created nothing.

## Grounding

- `get_job_log` (`east`, `693027`): composite `jobs` read. `log_trimmed_size` is the
  stored tail's byte length, which is at most `log_original_size` (SKILL.md ordering
  constraint).
- `get_job_events` (`east`, `693027`, `changed_only: true`): rows with matching
  job_id + controller, ordered by `counter`, filtered to `changed`. Three of the seven
  seeded rows survive. `event_count` = 3 and `filters` echoes `{failed_only: false,
  changed_only: true}`.
- `fetch_github_file agnosticd/agnosticd-v2
  ansible/configs/retail-edge-pos/files/cloud_providers/ec2_cloud_template.j2`. The
  path is in the log's render-task `src`, under `/runner/project`. Seeded under `HEAD`
  and `main`.
- Match is unordered-subset. The events call and the log call are siblings with no
  dependency; the fetch depends only on the log.

## Contract

- Required: `cfn-error` (log literal); `guard-gap` (derived, from the template);
  `key-pair` and `bucket` (events only).
- Count: `changed-tasks` = 3. This is cheap on purpose, because the retained recap also
  says `changed=3`; the names are what discriminate.
- Citation: line 38, `PublicSubnetBRouteTableAssociation:`, counted by `gen_104.py` from
  the seeded text.
- Forbidden fact `stack-resources` (VPC or subnet listed as created or to delete). No
  `attributed_to`.
- Weights 0.3/0.7. No forbidden calls.

## The wrong answer

> Unresolved resource dependencies [PublicSubnetB] ... looks like a typo for PublicSubnetA.
> 3 tasks changed ... the VPC was created, so delete the VPC and the stack resources.

`score.py --golden-calls` gives reward **0.50** (answer 0.286). It misses `guard-gap`,
`key-pair`, `bucket` and the line citation (the cited path has no line), and hits
`stack-resources`.

## Invented

Every literal is invented for bench-v5: job 693027, GUID `k9fhs`, the config
`retail-edge-pos` and its roles, the key pair, bucket and AMI ids, the fingerprint, the
CIDRs, the template and the git revision.
