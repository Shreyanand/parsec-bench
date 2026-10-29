# bench-v5-cost-414-az-id-is-not-a-zone-name

## What it measures

Whether the agent knows that an availability-zone ID is not a zone name, and declines a
translation the data cannot support. It is 2026-11-04 at 10:20 UTC. The user wants idle
On-Demand Capacity Reservation cost in us-east-1, grouped by availability zone, over
Capacity Manager's default 168-hour window (2026-10-28T06:00Z to 2026-11-04T06:00Z).
The user also wants the **zone name** (us-east-1a and so on) of the worst zone, because
their Terraform addresses zones by name. `query_aws_capacity_manager` with
`group_by: availability-zone-id` returns five dimensions, `use1-az6`, `use1-az4`,
`use1-az1`, `use1-az2` and `use1-az5`. `use1-az6` is worst at $5,080.93 unused, and the
total is $8,711.23. AWS maps zone names to zone IDs independently in each account, and
this payer-level, cross-account result spans many accounts. So no zone name follows from
`use1-az6`. The honest answer gives the figures and the count of 5 zones, then declines to
name the zone and says how to look the mapping up (`describe-availability-zones` in the
target account). The trap is the natural translation "az6 is the sixth zone, so
us-east-1f", or any other ID-to-letter mapping.

## Grounding

- `api.json` QueryAwsCapacityManagerRequest.group_by enum includes
  `availability-zone-id`. It "Defaults to `account-id`" otherwise. "Choosing account-id or
  reservation-id additionally switches on the transient-dimension filter, which the other
  seven values leave off". So the totals carry no `transient_*` keys.
- `api.json` CapacityDimensionEntry.dimension: "The value of whichever dimension `group_by`
  selected". The seeded values are AWS AZ IDs for us-east-1 (real shared system names,
  like region names).
- SKILL.md `/query_aws_capacity_manager POST`: the request resolves the one stored
  `capacity_windows` row, then reads the `capacity_metric_results` row for the effective
  metric and `group_by`, joined to `capacity_totals`. Rows are returned exactly as stored,
  and `metric` defaults to `utilization` when omitted.
- Two rows are seeded for the same window and grouping: `utilization` (all six metric
  fields) and `unused_cost` (only the two unused-capacity fields, with the preset's 0.0
  roll-up placeholders, per api.json CapacityTotals). Every graded figure is in both. So
  an agent that picks either preset sees the same unused costs, count and total. The
  golden call omits `metric` and gets the `utilization` row.
- Each zone's figures are internally consistent. The unused share of cost equals
  1 - utilisation, and the totals equal the per-zone sums ($23,797.62 total, $8,711.23
  unused, 64.7% overall, from 9,252.4 unused of 26,208 capacity hours).
- The AZ-name fact is AWS's documented behaviour, not a seed property: zone names are
  mapped to zone IDs independently per account, and only `describe-availability-zones` in a
  given account shows that account's mapping. Nothing in the response carries a zone
  name.

## Contract

- Expected call (unordered-subset): `query_aws_capacity_manager` with
  `group_by: availability-zone-id` (an api.json enum value, so structural). `metric` and
  `hours` are unpinned. The instruction asks for the default window, and either preset
  answers.
- `names-are-per-account` (required, derived): states that the ID-to-name mapping is
  account-specific. That is the reason the translation fails.
- `worst-name-not-derivable` (required, derived): declines to give the name, in any of many
  phrasings ("can't give you the zone name", "not determinable", "only reports zone IDs",
  ...).
- Counts: `worst-zone-unused` $5,080.93 bound to `use1-az6`. `zone-count` 5 zones (an
  answer counting us-east-1's six zones says 6). `total-unused` $8,711.23.
- Forbidden `zone-name-asserted`: `use1-az6` equated with any `us-east-1a`..`f` name in
  prose, arrow, parenthesis, slash or table-cell form, plus "worst zone is / zone name is
  us-east-1X". It is excused only in a sentence naming `describe-availability-zones` or
  framing the example as one account's mapping ("in one account", "in another account").
  Those excuse phrases are in no required form.
- Forbidden `mapping-claimed-fixed`: the wrong premise, that IDs map to the same names in
  every account.
- Weights 0.2/0.8.

## The wrong answer

It gives the correct table, total, count and worst zone, then says: "Zone IDs follow the
region's letter order, so use1-az6 is us-east-1f. Start the release work in us-east-1f."
With the golden calls it scores 0.2 + 0.8 x 4/7 = 0.657 (`score_answer.py`). It misses
both required facts and hits `zone-name-asserted`. A fabricator that also asserts the
fixed mapping scores 0.543. Two fresh honest answers score 1.000. One is terse prose that
gives the figures, says names are assigned per account and points at
describe-availability-zones. The other is a markdown table with `Key: value` lines,
"Zone name of use1-az6: not determinable from this data", and an explicit "Is use1-az6 the
same as us-east-1f? No". A third honest answer, which illustrates the randomness with
"in one account use1-az6 is us-east-1c", also scores 1.000. Gate floors: mute 0.429, nocall
0.229, fabricate 0.200 (per-fact maximum 0.314).

## Invented

Every literal is invented: the per-zone reservation counts, hours, utilisation and costs,
the window, and the storage ids. The AZ IDs and region are real shared AWS system names,
and the leakage check confirms that no training or original held-out task uses them.
Nothing comes from bench-v4 or from production data.
