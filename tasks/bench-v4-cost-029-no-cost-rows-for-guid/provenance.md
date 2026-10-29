# bench-v4-cost-029-no-cost-rows-for-guid

## What it measures

Whether the agent renders an absent cost row as `$0`. It is the money version of
`bench-v4-platform-023`'s silent Splunk window, and the consequence is more concrete:
someone in finance acting on a fabricated zero has been given a wrong number, not just an
unsupported theory.

## The store is populated, deliberately

The Azure result carries a real row for `pool-01-402` at $310. So the emptiness is specific
— "no row for pool-01-401" — rather than "the query returned nothing", which an agent could
reasonably read as a broken tool. `which-subscription` requires naming the subscription that
has no data, which is what forces that distinction to be made.

The neighbouring subscription number is one digit away on purpose: it makes "the mapping may
be wrong" a genuinely live explanation rather than a formality, and the golden answer says so.

## `subscriptions_queried` again

Set to `"all"`, the string form, for the same reason as `bench-v4-cost-028`: the generated
schema collapsed the spec's `["integer","string","array"]` union to `string`, so the integer
count parsec normally returns cannot be seeded. `CLAUDE.md` limitation 9.

## `attributed_to` in its second form: refusal, not attribution

The forbidden forms are bare (`$0`, `zero cost`, `0.00`) and stay that way — narrowing them
to whichever phrasing one imagines a fabricator using misses the others, which is the trade
`CLAUDE.md` limitation 8 spells out.

But an honest answer here does not merely avoid the figure; it names it in order to reject
it — "I am not going to render that as $0" — and the first draft's golden answer tripped its
own forbidden fact for exactly that. `attributed_to` is what resolves it, used for
**refusal** rather than attribution: a sentence carrying `not going to render`,
`an absent row`, `is not the same as` and the like is excused.

The phrases are deliberately long. A short cue like `is not` would be excused inside a
fabrication ("the cost is $0, which is not unusual"); these are not phrasings an inventing
agent produces. And the exemption is per sentence, so a refusal in one sentence cannot
license a figure asserted in another.

## Grounding

`query_azure_costs` requires `start_date` and `end_date` in `sim-specs/cost/openapi.json`.
`AzureCostResult.source` is enforced as `['cache', 'live']`, and `cache` is used here because
the cache-refresh timestamp gives one of the candidate explanations something concrete to
rest on.

## Absolute dates

The instruction names `2026-05-01` to `2026-05-31` rather than "last month", so the correct
answer does not change with the run date.

## Weighting

`0.2 / 0.8`. One call, both arguments given. Everything measured is the refusal to invent a
figure and the quality of the explanation offered instead.

## Invented

The GUID `rc9jt`, both subscription names, the $310 figure and every timestamp. **Nothing
comes from the gitignored trace export.**
