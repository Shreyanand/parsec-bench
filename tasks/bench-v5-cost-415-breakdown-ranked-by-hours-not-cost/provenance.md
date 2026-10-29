# bench-v5-cost-415-breakdown-ranked-by-hours-not-cost

## What it measures

Whether the agent ranks by the quantity it was asked about, instead of trusting the order
(and the `rank` column) a passthrough payload came in. The user wants the three costliest
AWS instance types for September 2026, their costs and their combined cost, for a slide
ordered most expensive first. `query_cost_monitor` `breakdown` with
`group_by: INSTANCE_TYPE` returns ten rows. Each has `rank`, `instance_type`,
`usage_hours` and `cost`, and they are ranked by **usage hours**: rank 1 is `m7i.xlarge`
with 46,800 hours but $8,985.60. Sorted by cost, the top three are `g5.4xlarge`
$12,862.08 (rank 6), `p3.2xlarge` $11,016.00 (rank 9) and `c7i.2xlarge` $9,302.40
(rank 2), together $33,180.48. The trap is to read rank 1-3 as the top three
(m7i.xlarge, c7i.2xlarge, t3.large, $20,444.54) and to call m7i.xlarge the most expensive.
The payload states its dates (all September), so there is no window problem. All of the
fleet's ten types are listed (fewer than the default `top_n` of 25), so there is no
truncation problem either.

## Grounding

- `api.json` `/query_cost_monitor` SIMULATION STORE AUTHORITY: "Select the stored row whose
  `endpoint` field equals the request's `endpoint`; the date and filter arguments do not
  select a row. ... Echo the `results` elements verbatim, with no field renamed, added,
  recomputed or summarised". SKILL.md Numeric Ranges: "Returned arrays preserve stored
  order; no numeric sort is applied by the simulator". So the hours order reaches the agent
  unchanged.
- SKILL.md Derivation Rules: with no `_dashboard_link` on the stored row, "the response is
  the stored `results` array itself, not an object". The golden result is the bare array.
- `api.json` CostMonitorResult: the upstream payload is unmodelled ("parsec describes none
  of it"). So the row fields (`rank`, `usage_hours`, `cost`, dates) are invented upstream
  content, as in the training seeds for this tool.
- Enums hit: `endpoint: breakdown`, `group_by: INSTANCE_TYPE` (api.json
  QueryCostMonitorRequest).

## Contract

- Expected call (unordered-subset): `query_cost_monitor` with `endpoint: breakdown` and
  `group_by: INSTANCE_TYPE`. The dates and `providers` are unpinned because the store
  ignores them.
- Counts: `first-g5` $12,862.08 bound to g5.4xlarge. `second-p3` $11,016.00 bound to
  p3.2xlarge. `third-c7i` $9,302.40 bound to c7i.2xlarge. `top3-combined` $33,180.48
  (derived, with a note). `third-c7i` is also rank 2, so the decoy reading earns it. That is
  recorded partial credit (bar C), not a discriminator.
- Forbidden `hours-rank-read-as-cost`: m7i.xlarge asserted as the most expensive, costliest
  or top spender, or the rank-order triple "m7i.xlarge, c7i.2xlarge and t3.large" given as
  the answer. It is excused only in a sentence that names the hours ordering ("by hours",
  "usage hours", "most hours", "instance-hours", ...). No required or count form contains
  any of those excuses.
- Weights 0.3/0.7, as the slot fixes.

## The wrong answer

"The top three instance types by cost: 1. m7i.xlarge — $8,985.60, 2. c7i.2xlarge —
$9,302.40, 3. t3.large — $2,156.54. So m7i.xlarge was the most expensive, and the three
together cost $20,444.54." With the golden calls this scores 0.3 + 0.7 x 1/5 = 0.44
(`score_answer.py`), equal to the mute floor. It keeps only the c7i.2xlarge figure and hits
the forbidden fact. A fabricator that names the rank triple without figures scores 0.300.
Two fresh honest answers score 1.000. One is terse prose saying the list is ordered by usage
hours. The other is a markdown table with a "Monitor rank" column and an explicit
"Is m7i.xlarge the most expensive? No." Gate floors: mute 0.440, nocall 0.140,
fabricate 0.300.

## Invented

Every literal is invented: the hours and costs, the rank order and the storage id. The
instance types are real AWS type names. The leakage check found none of them in any
training or original held-out task's identifiers (an earlier draft's m6i/c6i names were
replaced for that reason). Nothing comes from bench-v4 or from production data.
