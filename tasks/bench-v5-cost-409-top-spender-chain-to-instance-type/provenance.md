# bench-v5-cost-409-top-spender-chain-to-instance-type

## What it measures

A clean four-hop drill-down across three cost tools, where each hop's key comes from the
previous result:

1. `query_cost_monitor` `breakdown` (`group_by: LINKED_ACCOUNT`): the top account is
   `593027418866` (ml-training-prod) at $71,402.88, narrowly ahead of `448190265537` at
   $68,950.12. The narrow margin makes a guessed or skipped breakdown detectable.
2. `query_cost_monitor` `drilldown` (`account_services`, `selected_key: 593027418866`): EC2
   compute leads at $52,118.40.
3. `query_aws_costs` (`group_by: INSTANCE_TYPE`, that account): `g6e.12xlarge` $38,906.20.
   The $19,284.48 `NoInstanceType` bucket is the non-EC2 remainder, which is larger than
   the second instance type but is not an instance type. The three real types sum to the
   drilldown's EC2 figure, and the account total matches the monitor.
4. `query_aws_capacity_manager` (`account_id` filter, `group_by: instance-type`):
   `g6e.12xlarge` runs at 91.4% utilisation.

This is the group's happy task. Every tool answers consistently, and the score depends on
completing the chain with the right discovered arguments.

## Grounding

- SKILL.md `/query_cost_monitor POST`: rows are selected by `endpoint` alone, so the
  breakdown and drilldown rows are distinct by `endpoint`. With no `_dashboard_link`, the
  response is "the bare stored `results` array itself". `api.json` QueryCostMonitorRequest
  enums: `group_by` LINKED_ACCOUNT, `drilldown_type` account_services.
- SKILL.md `/query_aws_costs POST`: `periods` resolves 2026-09-01..2026-10-01 to
  `per-aws-v9t-2609`, and the row is returned as stored. `api.json` AccountCost.account_id: a
  12-digit id (not `org-wide`) arises when an account id is supplied "*and* group_by is
  SERVICE or INSTANCE_TYPE", which is this case.
- SKILL.md `/query_aws_capacity_manager POST`: resolves `capacity_windows`, then the
  `capacity_metric_results` row for metric `utilization` and `group_by` `instance-type`.
  "Apply request filters only by returning the stored row that matches the resolved
  request", so the stored row is the account-filtered result. No transient filter applies
  for `instance-type`. `overall_utilization_pct` 86.1 = (1 - 256/1848) x 100.

## Contract

- Expected calls (ordered-subsequence, a dependency chain), pinning only the discovered
  keys and the grouping arguments that are the point.
- Required: the top account, the top service and the instance type.
- Counts: the account's $71,402.88, `g6e.12xlarge`'s $38,906.20 and the 91.4% utilisation.
- No forbidden facts (happy task). Weights 0.3/0.7.

## The wrong answer

An agent that skips the breakdown and drills into the second account it sees (or stops at
EC2) misses most facts. "448190265537 is the top spender at $68,950.12. EC2 drives it, and
NoInstanceType is the largest instance-type line." With the golden calls this scores 0.3 +
0.7 x 1/6 = 0.42, keeping only `top-service`. With its own calls, which lack the
`selected_key`/`account_id` for 593027418866, the tool component drops too. The content-free
answer scores 0.00 of the answer component.

## Invented

Every literal is invented: the five accounts and names, every figure, the window and the
storage ids. Nothing comes from bench-v4 or from production data.
