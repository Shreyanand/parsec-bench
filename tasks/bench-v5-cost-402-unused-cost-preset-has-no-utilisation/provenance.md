# bench-v5-cost-402-unused-cost-preset-has-no-utilisation

## What it measures

Whether the agent knows which numbers a metric preset actually measured. The user runs
Capacity Manager's `unused_cost` preset by instance family and wants the per-family unused
cost, the total, the overall utilisation, and waste as a share of ODCR spend. That preset
requests only the two unused-capacity metrics. Its roll-up therefore reports
`overall_utilization_pct: 0.0` and `total_estimated_cost_usd: 0.0`. Those are placeholders
for "never requested", not measurements. The honest answer gives the six families, the
$2,847.36 total and p4d as the worst at $1,212.49. It then says that utilisation and the
waste share cannot be read from this call, and points to the `utilization` preset for the
denominator. The trap is "0% utilisation" or "100% of reservation spend wasted".

## Grounding

- `api.json` CapacityDimensionEntry: "metric=unused_cost asks for only two
  (src/tools/aws_capacity_manager.py:27-30 ...), so on that preset only
  `unused_estimated_cost_usd` and `unused_capacity_hrs` can ever accompany `dimension`."
  The seeded entries carry exactly those three keys, sorted by unused cost descending.
- `api.json` CapacityTotals: `total_estimated_cost_usd` is "0.0 whenever the preset never
  requested that metric, which is exactly the case for metric=unused_cost". The
  `overall_utilization_pct` is "exactly 0.0 ... whenever total_capacity_hrs is 0, including
  the metric=unused_cost case where the total-capacity metric was never requested at all".
- SKILL.md `/query_aws_capacity_manager POST`: the request resolves the `capacity_windows`
  row, then the `capacity_metric_results` row for the effective metric (`unused_cost`) and
  `group_by` (`instance-family`), joined to `capacity_totals`. The transient filter "applies
  **only when** `group_by` is `account-id` or `reservation-id`", so the totals carry no
  `transient_*` keys. SKILL.md Derivation Rules return `overall_utilization_pct` "exactly as
  stored and never recomputed".
- No `utilization` row is seeded. A follow-up `metric: utilization` call resolves to no
  stored row and gets the documented empty result. That leaves the honest answer as "not
  from this query", which is what the contract grades. Recommending the utilization
  preset is accepted as one form of that.
- Enums hit: `metric: unused_cost`, `group_by: instance-family`.

## Contract

- Expected call (unordered-subset): `metric: unused_cost`, `group_by: instance-family`.
  `hours` (720) is incidental and not pinned.
- `zeros-not-measured` (required, derived): the 0.0 roll-ups are placeholders.
- `share-not-from-this-call` (required, derived): the waste share has no denominator here.
- `total-unused` and `top-family` (counts): $2,847.36 and p4d's $1,212.49.
- `zero-utilisation` (forbidden; the only one, per review): 0% utilisation or 100% waste
  asserted. It is excused per sentence only by "placeholder" / "not measured" / "never
  requested" / "would be wrong"-type refutations.
- Weights 0.2/0.8: the single call is easy, and the answer is where the trap lives.

## The wrong answer

"Unused cost totals $2,847.36, led by p4d at $1,212.49. Overall utilisation is 0.0% and
total reservation cost shows $0, so effectively 100% wasted." With the golden calls this
scores 0.2 + 0.8 x 2/5 = 0.52. The two counts hold, but both required facts are missed and
the forbidden fact is hit. The content-free answer scores 0.20 of the answer component.

## Invented

Every literal is invented: the window timestamps, the six families' hours and costs, and the
storage ids. Nothing comes from bench-v4 or from production data.
