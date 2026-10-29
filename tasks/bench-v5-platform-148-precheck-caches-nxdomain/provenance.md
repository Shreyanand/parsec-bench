# bench-v5-platform-148-precheck-caches-nxdomain

## What it measures

A four-call RCA on a failure class no existing task has: **DNS negative caching
caused by the automation's own lookup**. The role first checks that the cluster's API
name is free by resolving it through the VPC resolver, and gets NXDOMAIN with the zone's
SOA (TTL 900). Two seconds later it creates the record, and Route 53 reports the change
`INSYNC`. It then waits on the same resolver for 20 x 15 = 300 seconds. The resolver
keeps answering from its negative cache for 900 seconds, so the wait times out with
NXDOMAIN while Route 53 serves the record.

The instruction voices the obvious reading: Route 53 is not propagating new records,
and the remedy is an AWS support case. The log refutes it (INSYNC 4 s after the
UPSERT). The cause is a combination no single string states: a lookup *before* the
record existed, the SOA TTL printed in that lookup's AUTHORITY line, and a wait budget
that only the defaults give.

## Tranche

**Challenge.** Expected to score below 1.0 for a good agent. The agent failure it
exposes is **treating the loud symptom's subject as the culprit and the automation as
an innocent observer**: NXDOMAIN after a record change reads as a DNS-side fault, and
the step that poisons the cache is a harmless-looking safety check that *succeeded*.
Good agents commonly see INSYNC and say "propagation is fine, the wait is too short"
without the negative cache, the 900-second TTL or the pre-check.

## Grounding

- `query_aap2 get_job_log`: composite `job_id` + `controller` on `jobs`; the row carries
  `git_url`, `git_branch` and `git_revision`, so the repository and revision come from
  the result.
- `search_github_repo` (github SKILL.md): reads only `repo_search_results` by exact
  `(owner, repo, ref, search)`, an omitted `ref` resolving to `HEAD`. The role name is
  in every `task path:` line of the log; four search spellings of it
  (`infra_dns_api_record`, with and without the `roles_infra/` or `ansible/roles_infra/`
  prefix, and with a trailing `/`) are seeded under `HEAD`, `main` and the job's
  `git_revision`, each returning the two role files. Search is exact-key, so an agent
  searching another string gets `matches: []`; the expected call pins only `owner` and
  `repo`, and both expected fetch paths stay reachable without the search (the tasks
  path is in the log's `task path:` lines, the defaults path is the role's
  conventional `defaults/main.yml` and is in the seeded search result).
- `fetch_github_file`: both role files are seeded under `HEAD`, `main` and the job's
  `git_revision`, so a fetch with no `ref`, with `main` or with the revision returns the
  same content.
- Controller `west` is an api.json enum value.

## Contract

Weights 0.3 / 0.7, `unordered-subset`: the two fetches and the search are siblings once
the log has given the repository; each pinned path already forces its dependency.

- `record-insync`: Route 53 had the record, in the log.
- `negative-ttl`: 900 seconds, in the log's AUTHORITY line only.
- `negative-cache` (derived): the resolver cached the NXDOMAIN.
- `precheck`: the role's pre-check lookup (task in the log and tasks file, flag in the
  defaults).
- `not-propagation` (derived): the decoy refuted.
- count `wait-budget` = 300 seconds (window 3), with `5 minutes` and `20 x 15` forms in
  `extra_any_of`.
- forbidden `propagation-blame` (with `attributed_to` only for sentences naming the
  user's theory) and `resolver-down`, written as claims (hazard 22).

Mute answer floor: 2 forbidden of 8 answer items, reward 0.475.

## The wrong answer

`/tmp/ext/scratch/bench-v5-platform-148-precheck-caches-nxdomain/wrong.md`: reads the log, sees NXDOMAIN after the UPSERT, says
Route 53 is slow to propagate and backs the AWS case. With the golden calls it scores
**0.5625**: it earns two true literals (`record-insync` from the UPSERT, and the 300-second
wait budget), which is partial credit under bar C, not a defect. A resolver-blaming variant
(`wrong2.md`) scores 0.475. Golden 1.000.

Honest panel, all **1.000**: two authored answers (`honest1-2.md`: prose, and a table that
denies propagation) and three blind answers by a separate agent from the instruction and
the tool results only (`blind-a/b/c.md`). One blind answer first scored 0.9125 ("Route 53
behaved correctly"), so `not-propagation` was widened; table-cell denials ("propagate? |
No") are also enumerated.

## Invented

Every literal is invented: job 6173904, GUID `zk5rd`, the catalog item
`service-interconnect-lab`, the zone `sbxlab.example.net`, the role
`infra_dns_api_record` and its variables, the resolver and record addresses, the
Route 53 change id, the name-server name in the SOA line, the revision and every
timestamp and figure. The incident class (an existence pre-check that negatively caches
a name the job is about to create) is invented in the mould of bench-v4's challenge
tranche; no public postmortem is its source, and nothing comes from bench-v4 or
production data.
