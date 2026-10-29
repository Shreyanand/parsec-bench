# bench-v4-cost-030-threshold-not-an-anomaly

## What it measures

Deciding that a fired threshold is *not* an incident, and doing it from a baseline rather
than from the alert. The seed is built so the wrong comparison gives the wrong answer:
against last month, June 2026 is a 2.5x jump and looks alarming; against the same month a
year earlier it is a 5% increase and is plainly seasonal.

`prior-year` is the fact that separates the two. An agent that queries only June and May
can still produce a confident-sounding answer, and it will be the wrong one.

## Grounding

`vendor/parsec/skills/cost-anomaly-triage/SKILL.md` supplies the verdict vocabulary: its
own description says the skill must "decide whether it is expected seasonality, a
legitimate new workload, or an incident", and it is explicit that it is "not for 'why did
the bill go up', which already assumes the answer". The instruction offers exactly those
three outcomes.

`query_cost_monitor` requires `endpoint`, `start_date` and `end_date`, and **`endpoint` is
an enum of four dashboard views** — `summary`, `breakdown`, `drilldown`, `providers` — not a
free-form monitor name. The first draft passed `aws-monthly` and `seedcheck`'s `golden-args`
check refused it against `api.json`. Another surviving enum, alongside the ones
`bench-v4-cost-028` hit.


`query_aws_costs` requires `account_ids`, `start_date` and `end_date`;
`query_aws_capacity_manager` requires nothing. All from
`sim-specs/cost/openapi.json`. `CapacityTotals` requires
`overall_utilization_pct` and `unused_estimated_cost_usd`, which is what lets the capacity
leg rule out waste as an explanation.

This is the suite's only `query_cost_monitor` scenario and its only
`query_aws_capacity_manager` scenario.

## Why the utilisation figure is a required count

97.7% utilisation with $1,100 unused is what distinguishes "expensive because busy" from
"expensive because wasteful". Without it the seasonality verdict rests on the year-over-year
comparison alone; with it, the second candidate explanation is actively excluded rather than
ignored. The count is declared as `97` with `extra_any_of: ["97.7"]`, since that is how the
figure is actually written.

## Three absolute periods

Every date is absolute in both the instruction and the seed, including the year-earlier
comparison. A relative phrasing ("the same month last year") in the instruction would age:
the seeded periods are fixed, so which months they are must be too.

## Weighting

`0.3 / 0.7`. Five calls, but every argument is handed over by the instruction; what is
measured is the reasoning across four results and the refusal to escalate.

## Invented

Every figure, the account id, the monitor endpoint, the dashboard link and all three
periods. **Nothing comes from the gitignored trace export** — the one real
`query_cost_monitor` call there returned no data this scenario uses.
