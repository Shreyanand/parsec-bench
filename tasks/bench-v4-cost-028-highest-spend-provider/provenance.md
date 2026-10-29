# bench-v4-cost-028-highest-spend-provider

## What it measures

A cross-provider comparison that cannot be answered from one call. Three tools, one period,
and a winner that is only knowable after all three have been queried — the two loser totals
are required facts precisely so that skipping a call is detectable.

## The union collapse, and the form the seed is forced into

`AzureCostResult.subscriptions_queried` is `{"type": "string"}` in
`harness-skills/parsec-cost/schema.json`. `sim-specs/cost/openapi.json` declares it as
`{"type": ["integer","string","array"]}`, because parsec's two return paths genuinely
disagree — the main assembly sets the *count* of supplied subscription names, or the literal
`"all"` when none were supplied (`src/tools/azure_costs.py:242`, `:136`), while the no-blobs
early return sets the supplied *list* (`:186`).

Generation has no representation for a union and collapsed all three to `string`. So this
seed uses `"all"`, which is the form the generated `db.json` itself uses, and **the integer
count parsec normally returns cannot be seeded at all**. That is `CLAUDE.md` limitation 9,
and this is the scenario it bites. The spec is right and the generated schema is the lossy
half; the spec is deliberately not widened to match.

## Why `extra_any_of` carries the comma-grouped totals

Every total here is five figures, and any real answer writes `$21,900` rather than `21900`.
The numeral matcher works on digit runs, so `21,900` would be rejected by the
thousands-separator guard — correctly, since that guard is what stops `1,300` matching `300`.
`extra_any_of` is the escape hatch the count matcher provides for exactly this, and it is
used rather than loosening the guard.

## Three constraints the generated schema imposed

Two enums **survived** generation and are enforced: `AzureCostResult.source` is
`['cache', 'live']` (the first draft seeded `'blobs'`) and `GcpCostResult.group_by` is
`['SERVICE', 'PROJECT']` (the first draft seeded lowercase `'service'`). Worth recording
next to the losses in `LOST_IN_GENERATION` — response-shaped enums do reach the store.

And `query_aws_costs` requires `account_ids`, which the first draft's golden call omitted;
`seedcheck`'s `golden-args` check caught it against `api.json`. The instruction now names
the two accounts in scope, since a required argument the instruction never supplies would
make the call guesswork.

## Grounding

`query_aws_costs`, `query_gcp_costs` and `query_azure_costs` all require `start_date` and
`end_date` in `sim-specs/cost/openapi.json`. The question is a real trajectory's verbatim
shape ("Which cloud provider are we spending the most on this month, and what are the top 3
services driving that cost?") — with "this month" replaced by an absolute range, since the
wall-clock rule forbids the original phrasing.

`cost` is the thinnest service in the corpus: three traces touch it at all, and only one is
cost-only. This scenario and the two after it exist to cover five modelled tools, which is
why the design document says the suite mean is not workload-weighted.

## Weighting

`0.3 / 0.7`. Three calls whose arguments are all handed over, so no call is a discovery; the
answer carries seven facts, three of which each prove a different call happened.

## Invented

Every figure, both AWS accounts, all service and subscription names, and the period.
`NCasT4_v3` and `Dsv5` are real Azure VM series names used as ordinary seed literals.
**Nothing comes from the gitignored trace export.**
