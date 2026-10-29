# bench-v5-cost-403-capacity-results-truncated-at-50

## What it measures

Whether the agent notices that a list it was handed is cut off. Grouped by instance type,
Capacity Manager has 63 surviving dimensions. `results` holds the worst 50 by unused cost,
`totals.results_truncated` is `true`, and `totals.total_dimensions` is 63. The totals cover
all 63: $26,017.15 unused, against $25,590.78 for the 50 listed rows. The honest answer
reports 63 instance types and the totals figure. It then says the five least-wasteful
types cannot be named, because the list is sorted worst-first and the 13 smallest are
exactly the rows that were cut. The trap is to count the list (50), sum it, and name its
last five rows as the "least unused".

## Grounding

- `api.json` CapacityDimensionEntry: "Entries are sorted by `unused_estimated_cost_usd`
  descending ... and the list is then capped at 50".
- `api.json` CapacityTotals: `total_dimensions` is "len(results) at the moment this dict is
  built ...: after transient dimensions were dropped, but before the 50-entry cap. So it can
  exceed the length of `results`". `results_truncated` is "Present, and then always true,
  only when more than 50 dimension entries survived and the list was cut to 50". The cost
  roll-ups accumulate across every surviving dimension.
- SKILL.md `/query_aws_capacity_manager POST`: the transient filter applies "**only when**
  `group_by` is `account-id` or `reservation-id`". Store reads resolve `capacity_windows`,
  then `capacity_metric_results` by window + metric (default `utilization`) + `group_by`,
  joined to `capacity_totals`. SKILL.md Derivation Rules: `total_dimensions` and
  `results_truncated` are "returned exactly as stored". "Returned arrays preserve stored
  order", and the stored order is the sorted one.
- Generator: `.scratch/gencost/t403.py` builds 63 types, sorts them, stores the first 50,
  and computes the totals over all 63. `overall_utilization_pct` (75.9) is
  `(1 - unused_hrs/total_hrs) * 100` over all 63.
- Enum hit: `group_by: instance-type`.

## Contract

- Expected call (unordered-subset): `query_aws_capacity_manager` with `group_by:
  instance-type`. `metric` is not pinned, since the default and an explicit `utilization`
  are equivalent.
- `list-truncated` (required): the cap or truncation is named.
- `bottom-five-unknowable` (required, derived): the least-wasteful five are among the cut
  rows.
- `instance-types` (count 63) and `total-unused` (count $26,017.15).
- `fifty-types` (forbidden): "50 instance types", excused only by sentences that set 50
  against 63 or name the cap.
- Weights 0.2/0.8.

## The wrong answer

"We hold reservations for 50 instance types, with $25,590.78 unused in total. The five with
the least unused cost are g5.12xlarge, trn1.12xlarge, inf2.12xlarge, x2idn.12xlarge and
r7i.12xlarge." With the golden calls this scores 0.2 + 0.8 x 0/5 = 0.20. A variant that
quotes the totals figure but still counts 50 scores 0.2 + 0.8 x 1/5 = 0.36. The
content-free answer scores 0.20 of the answer component.

## Invented

Every literal is invented: the window, the 63 instance-type rows and all their figures
(generated), and the storage ids. Nothing comes from bench-v4 or from production data.
