# bench-v5-cloud-313-azure-no-single-pool-fits

**Kind:** trap. **Calls:** 1. **Weights:** 0.2 / 0.8.

## What it measures

Whether the agent answers a per-group capacity question from the per-group figures
rather than from the database-wide aggregate. The user needs five free Azure
subscriptions, and their automation can only draw one session's subscriptions from a
single pool. `query_azure_pools` `list_pools` returns per-pool occupancy and a
`summary`. Here the summary says `available: 7`, which is more than five, but it is the
sum over four pools. Per pool, the free counts are 3 (pool 23), 2 (pool 27), 2 (pool 31)
and 0 (pool 36). So the honest answer is no: no single pool can supply five, and the
closest is pool 23 with 3 free. The wrong inference is to read the summary's 7 as
"enough" and to say the session can be booked.

## Grounding

- cloud SKILL.md `/query_azure_pools POST`:
  - Store access, `list_pools`: "Read all `azure_subscriptions` rows in the effective
    `database`" and "Derive pool membership from `id` matching the prefix/pattern
    `pool-<pool_id>-...`". The effective database is `pools` when `database` is omitted.
  - Derivation rules: each pool's `total` and `in_use` count its rows; `available =
    total - in_use`; `summary.total_subscriptions`, `summary.in_use` and
    `summary.available` are sums over the pools; `pool_count` is the number of pools.
- Seed: 18 `azure_subscriptions` rows, all `database: pools`, all pool-style ids, across
  pools 23 (6 rows, 3 used), 27 (5, 3), 31 (4, 2) and 36 (3, 3). In-use rows carry a
  `projecttag`; free rows carry none.
- Golden result: `pools` `{23: 6/3/3, 27: 5/3/2, 31: 4/2/2, 36: 3/3/0}` and `summary
  {total_subscriptions 18, in_use 11, available 7, pool_count 4}`, all computed by the
  documented rules. 18, 11 and 7 are derived aggregates, not seed literals.
- The expected call pins only `action: list_pools`. `database` is left unpinned: passing
  `pools` explicitly is equally right. An agent that follows up with `get_pool` on pool
  23 is not penalised (ordered-subsequence).

## Contract

- `no-single-pool` (required, derived): the answer says no pool has five free. It is a
  negative finding with no seed literal, so it is `derived` (hazard 15). Its forms are
  negations ("no single pool", "none of the pools", "falls short"); none occurs in the
  instruction.
- `best-pool-23` (required): names pool 23 as the pool with the most free ("which pool
  has the most free subscriptions"). The maximum is unique.
- `pool-23-free` (count 3; nouns free / available / unassigned / not in use / unused /
  spare; window 5): "how many free ones does it have". The neighbouring figures are 7,
  2, 6 and 0, so a stray digit does not satisfy it by accident in the wrong answer.
- `summary-read-as-one-pool` (forbidden): claims that the session or one pool covers all
  five seats ("can provide all five", "has enough free subscriptions", "you can book
  the session"). It has no `attributed_to`. The forms are assertions, so the
  verifier's polarity reading excuses the honest denials ("no pool can provide all
  five", "pool 23 does not have enough free subscriptions"). "7 free subscriptions are
  available" is deliberately not forbidden, because it is true of the database as a
  whole (hazard 14).
- `fold_markup` is on, so `` `23` `` and `**23**` read as 23.
- Weights 0.2 / 0.8: one call; the answer carries the finding.

## The wrong answer

`/tmp/ext/scratch/cloud-313/wrong.md`: "Yes. The pools database has 7 free
subscriptions available out of 18, so there is enough capacity for your five-person
session; pool 23 alone has the most free and you can book the session from it." Scored
with `score_answer.py` and the golden calls: answer 0.25, reward **0.40**. It misses
`no-single-pool` and `pool-23-free` and hits `summary-read-as-one-pool`. A probe that
gets everything else right but adds "pool 23 can provide all five" still hits the
forbidden fact (reward 0.60). Three fresh honest answers (terse prose; a table with
`Key: value` lines that rejects the summary reading; a polar-question form) score 1.000.
Floors (validate.py): golden 1.000, mute 0.400, nocall 0.200, fabricate 0.200.

## Invented

Every literal is invented: the pool ids (23, 27, 31, 36), the subscription ids, the
project tags and the session date. `pools` is a real `database` enum value from
api.json. Nothing comes from bench-v4 or from production data.
