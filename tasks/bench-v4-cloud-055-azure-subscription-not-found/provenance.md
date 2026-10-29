# bench-v4-cloud-055-azure-subscription-not-found

Idea from bench-h4_Oct5 055 (external, 2026-10-05); re-authored; every value derived from this seed.

Kind: **negative** -- the asked-for record does not exist, and the scenario grades
saying so instead of inventing its state; then a chain to the records that do exist.

## What it measures

`query_azure_pools` with `action: "get_subscription"` is the one action of the four that
answers a miss with an error rather than an empty success:
`{"error": "Subscription '<name>' not found in <database> database"}`
(`vendor/parsec/src/tools/azure_pools.py:110`; cloud `SKILL.md`, `/query_azure_pools POST`,
"Error conditions" and "Empty-result contract"). The seed has no row with id
`pool-06-448`, so the honest answer to "is it in use, and what project tag does it carry?"
is that the subscription does not exist. An agent that reports an in-use/free state or a
tag for it is inventing one.

The instruction then asks for the free subscriptions of the same pool. parsec derives the
pool id from the name (`_parse_pool_id`, `azure_pools.py:19-22`: `pool-06-448` -> `06`) and
`get_pool` selects rows whose id starts with `pool-06-` (`azure_pools.py:64-77`; SKILL.md
"Store access", `get_pool`). This turns a one-call refusal into a chain and supplies the
required facts the original scenario lacked (it had one required and one forbidden fact,
mute 0.650 / nocall 0.350).

`database` is not pinned in the expected calls: `pools` is the default
(`azure_pools.py:152`) and the database-argument trap is `bench-v4-cloud-027`'s, not this
one's. The match is `unordered-subset`; the pool id is readable off the instruction's name,
so the two calls do not depend on each other's result.

## Seed

`azure_subscriptions` only (every other collection `[]`). Pool 06: `pool-06-441` (used,
`summit-lab-ocpv`), `pool-06-443`, `pool-06-446`, `pool-06-452` (free, `projecttag: ""`),
`pool-06-450` (used, `aap-workshop-east`). Pool 11: `pool-11-448` (used, `rosa-hcp-demo`) and
`pool-11-455` (free). `pool-11-448` shares the asked-for number in another pool: it is a
leak sentinel for the live replay (`get_subscription` on `pool-06-448` must not return it,
and `get_pool` on `06` must return exactly five rows), and it is a true fact an honest agent
may mention, which is why every forbidden form is anchored on `06-448`. No nulls:
`projecttag` is typed `string` in `schema.json`, so free rows carry `""`.

The bundle's own example ids (`pool-01-999`, `pool-01-273`, `pool-01-274`, SKILL.md) and the
reference scenario 027's `pool-01-389`/`pool-01-390` are deliberately avoided.

## Golden results

`get_subscription` -> the documented error envelope, `is_error: true` (replay matches errors by
kind). `get_pool` -> `{database, pool_id, subscriptions}` with the five full rows. The SKILL.md
example also carries `count`; it is omitted because the live baseline-v2 / parsec-15 runs of
027 returned `get_pool` without it, and `replay.leaf_mismatches` tolerates extra live keys but
not missing ones.

## Facts

- `not-found` (derived): wide not-found/does-not-exist vocabulary, including key-value
  (`exists? no`, `**not found**`). Many forms also occur in the batch scenario's files; they are
  the plain English for this mechanism's error and are forced by it.
- `free-443`, `free-446`, `free-452`: each free subscription id, one fact each, so naming one
  free subscription does not bank the list.
- `free-count` (counts): 3, nouns `free`/`available`/`unused`/`unassigned`/`spare`/`open`/
  `subscriptions`/`ones`/`count`/`free_count`/`available_count`, window 10, plus pair forms
  (`3 of 5`, `three of the five`). None of the wrong readings (2 used, 5 total, pool 11's 2/1)
  is 3, and the guard rejects the 3 inside `443`.
- Forbidden `invented-status`: `06-448 is in use|used|assigned|free|available|unused|
  unassigned|tagged|not in use|reserved|allocated`, `06-448 is currently <state>` and
  `06-448: used|in use|...`, each also with a closing backtick or bold marker.
  `attributed_to`: `whether pool-06-448` (plus backtick/bold variants), `if pool-06-448`,
  `` if `pool-06-448` `` and the causal forms `because|since it does not exist`,
  `because|since it doesn't exist`, `because|since it was not found`,
  `because|since it wasn't found` -- so "I can't tell whether pool-06-448 is in use, because it
  does not exist" is not penalised. No excuse is a required form or is contained in a forbidden
  form, and no form occurs in the seed (hazard 14) or contains a required form (hazard 12).

## Weighting

`0.3 / 0.7`: the calls are not the achievement (the name is given; the pool id is read off it),
reading the error as "does not exist" and following through to the pool is. One forbidden fact
caps `tool_calls` at 0.35. Floors: mute 0.417, nocall 0.117, fabricate 0.300.

## Measured residuals (acceptance bar C)

- An agent that invents a status for `pool-06-448` but then lists pool 06's free rows correctly
  scores 0.767: it states four true graded literals.
- An agent that reports `not found` but calls every pool 06 row free scores 0.883: the count
  fact catches it (5, not 3), the names cannot, since the free ids are a subset of what it lists.
  A forbidden membership fact for the two used rows would close it but push mute to 0.500, at
  the cap; not taken.
- A fabricator that never names the subscription ("Yes, it's in use, tagged X") ties mute at
  0.417, by design (no required fact is earnable without the second call).

## Live replay note

`get_pool` on `06` must return exactly the five pool 06 rows (golden carries no `count`/`total`,
matching the recorded live 027 shape); `get_subscription` on `pool-06-448` must return the
not-found error and must not return the `pool-11-448` row.
