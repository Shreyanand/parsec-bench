## What it measures

Cross-cluster aggregation over `list_resource_pools`, where a name search catches a same-prefix twin. On both `condor` and `merlin`, `search: rhel-edge-pool` returns two rows: `rhel-edge-pool` and `rhel-edge-pool-canary`. The `search` filter is a substring test on `name`. The agent has to keep the exact pool on each cluster and:

- report each one's `provider_name` (condor `rhel-edge-aws`, merlin `rhel-edge-azure`)
- sum `min_available`: 8 + 6 = 14
- sum `resource_handle_count`: 11 + 9 = 20

Including the canaries gives 17 and 25.

## Grounding

- platform SKILL.md `/query_babylon_catalog`: `list_resource_pools` reads `babylon_resource_pools` filtered by `cluster`, and ignores the request `namespace`. The `search` filter is over `name` (case-insensitive substring, "Optional inputs"). Rows are projected to `name, namespace, min_available, max_unready, lifespan, resource_handle_count`, "plus `provider_name`, `resource_name` when stored".
- Constraints: `min_available <= resource_handle_count` and `max_unready <= resource_handle_count` hold for every row.
- `cluster` is a free request string, and every row carries `cluster` and `namespace: poolboy`.
- Number choice: the graded values are {14, 20} plus two provider strings. No single row value is 14 or 20, and the canary-inclusive sums (17, 25) are forbidden. The canary providers (`edge-canary-*`) do not contain the graded provider strings.

## Contract

- Calls, `unordered-subset`: `list_resource_pools` on condor and on merlin, cluster pinned and `search` unpinned (an unfiltered list works too).
- Required: both provider names.
- Counts (derived): 14 min_available, 20 handles.
- Forbidden fact `canary-summed`: 17/25 phrasings. It has no excuses, because an honest answer that mentions the canaries quotes their per-pool values, not those totals.
- Weights 0.3/0.7.

## The wrong answer

`.scratch/probe/134-wrong.md` sums every row the search returned ("min_available of 17 and 25 resource handles") but names the providers right. It scores **0.58** with the golden calls: both counts missed and the forbidden fact hit.

## Invented

The pool names, providers, sizes and the clusters `condor`/`merlin` are invented. `poolboy` is parsec's own constant, shared vocabulary. Nothing comes from bench-v4 or production data.
