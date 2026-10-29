# bench-v5-cloud-308-azure-leftover-tag-on-free-sub

**Kind:** trap. **Calls:** 2. **Weights:** 0.3 / 0.7.

## What it measures

A two-hop Azure pool read in which the second hop holds a field contradiction. First,
`list_pools` picks the pool with the fewest free subscriptions from the occupancy counts:
pool 08 has 2 available, against 4 in pool 12 and 3 in pool 15. Then `get_pool` on `08`
lists the subscriptions.

Pool 08 has two free (`used: false`) rows. One of them, `pool-08-317`, still carries the
project tag `retail-ai-lab`. That tag is left over from a released assignment; the live
retail-ai-lab subscription is `pool-08-322`. `used` is the assignment flag, and the
pool's own `available: 2` agrees with it. An agent that reads "has a project tag" as "in
use" reports a single free subscription, and the waiting team gets half the capacity.

## Grounding

- cloud SKILL.md `/query_azure_pools POST`:
  - list_pools reads every `pools` row whose `id` matches `pool-<id>-...`. Non-matching
    names are excluded (seed row `aro-shared-legacy-3` is excluded for that reason).
  - It returns `pools` keyed by id with `{total, in_use, available}` and a `summary`.
  - get_pool returns `{database, pool_id, subscriptions[{id, used, projecttag}], total,
    in_use, available, truncated}`, with "`projecttag` when present on the stored row".
- Derivation rules: `in_use` counts rows with `used = true`, and `available = total -
  in_use`. The tag plays no part, so the simulation's own counts say 2.
- The expected calls pin `action`, plus `pool_id: "08"` as a string. verify.py compares
  strings exactly, and `"8"` would build the prefix `pool-8-`.
- **WARN justified:** 17 is `summary.total_subscriptions`, the documented sum over pool
  totals (SKILL.md derived fields), not a seed value.

## Contract

- Required:
  - `tightest-pool`: pool 08.
  - `free-325`, `free-317`: the two free subscription ids.
  - `leftover-tag` (derived): explains that the tag on 317 is left over or stale.
- Count `free-in-08` = 2 (nouns free / available / subscriptions).
- Forbidden `tag-read-as-used`: asserting pool-08-317 is in use, taken, assigned or
  unavailable, or that only one subscription is free. `attributed_to` is limited to
  naming the tag as leftover or stale, or saying it only "looks taken". Probe
  `.scratch/wrong/p308.md` ("Although the flag says otherwise, pool-08-317 is in use.")
  is hit; reward 0.88.
- Floors: mute 0.17, echo 0.17.

## The wrong answer

`.scratch/wrong/w308.md`: "pool-08-317 is assigned (it carries the retail-ai-lab project
tag), so only pool-08-325 is free". With golden calls: reward **0.65**. It misses
leftover-tag and the count, and hits the forbidden fact.

## Invented

Every literal is invented: subscription ids, pools and project tags. Nothing comes from
bench-v4 or from production data.
