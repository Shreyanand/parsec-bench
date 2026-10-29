# bench-v5-cost-417-commit-usage-excludes-tax-and-support

## What it measures

Whether the agent applies a stated exclusion rule to the line items of each provider's
result, instead of quoting the providers' totals. The user is preparing committed-use
discount talks and needs October 2026 usage-only spend per cloud, with tax and
support-plan fees removed, plus the three-provider usage total. Three sibling calls:

1. `query_aws_costs`, org-wide (`account_ids: []`), 2026-10-01..2026-11-01 (exclusive end
   stated in the instruction), SERVICE grouping. One `org-wide` entry with seven items.
   Five are usage (EC2 compute $61,384.20, RDS $18,902.55, S3 $9,471.30, EKS $6,215.75,
   CloudWatch $2,140.60). Two are not: **`Tax` $8,456.12** and **`AWS Support (Business)`
   $7,318.45**, each a single daily entry on 2026-10-01. `total_cost` is $113,888.97 and
   includes both.
2. `query_azure_costs`, all subscriptions, 2026-10-01..2026-10-31: cache path, two
   subscriptions, $33,903.25, usage meters only.
3. `query_gcp_costs`, 2026-10-01..2026-10-31: four services, $26,362.55, usage only.

The honest answer gives AWS usage $98,114.40 (the total less both lines), names the two
removed amounts, keeps Azure and GCP as they are, and totals $158,380.20. The trap is to
quote each provider's `total_cost` and sum them to $174,154.77, or to remove only the
`Tax` line ($106,570.52 for AWS).

## Grounding

- cost SKILL.md `/query_aws_costs POST`: `periods` resolves 2026-10-01/2026-11-01 to
  `per-aws-q4n-2610`. `aws_cost_results` is read by that `period_id` and returned exactly
  as stored. api.json AccountCost.account_id: one grouping key (no account filter) gives
  `org-wide`. Items use DimensionCost `{cost, daily}`. Each usage service's 31 daily
  entries sum exactly to its `cost`. Tax and support carry one entry each, because Cost
  Explorer returns a group only on days where it has cost. `accounts_queried` is 1, per
  the SKILL.md derivation rule (the number of returned `results` entries). `total_cost` is
  the sum of `results[].total`.
- cost SKILL.md `/query_azure_costs POST`: `azure_cost_results` is non-empty, so the cache
  path is taken. `periods` resolves 2026-10-01/2026-10-31 to `per-cal-q4n-2610`, and the
  row is returned as stored (`source: cache`, `subscriptions_queried: "all"`).
- cost SKILL.md `/query_gcp_costs POST`: the same period, `group_by` defaulting to SERVICE,
  so it selects `gcr-q4n-2610-svc`. It is projected to `breakdown`, `daily_rows`,
  `group_by`, `period` and `total_cost`.
- Enums hit: AwsCostResult.group_by `SERVICE`, AzureCostResult.source `cache`,
  GcpCostResult.group_by `SERVICE`.

## Contract

- Expected calls (unordered-subset, independent siblings): the three queries with the
  dates and the empty account list the instruction states.
- Required: `aws-usage-only` (derived, $98,114.40), `aws-tax-line` ($8,456.12),
  `aws-support-line` ($7,318.45), `azure-usage` ($33,903.25), `gcp-usage` ($26,362.55).
- Count: `three-provider-usage-total` $158,380.20 (derived, with a note).
- Forbidden: `gross-total-as-usage`. The billed totals summed ($174,154.77), which is in no
  seed. A sentence that labels it as the billed or gross figure ("including tax", "gross",
  "billed total", "still includes", "before removing") is excused.
- Weights 0.3/0.7. Every call is fully specified by the instruction, and the
  discrimination is in the answer.

## The wrong answer

"October usage: AWS $113,888.97, Azure $33,903.25, GCP $26,362.55. None of the providers
broke out tax or support separately, so nothing was removed. Usage total across the
three: $174,154.77." With the golden calls it scores 0.3 + 0.7 x 2/7 = 0.500
(`score_answer.py`). It keeps the Azure and GCP figures. It misses the AWS usage figure,
both removed lines and the usage total, and it hits the forbidden gross total. The variant
that removes only `Tax` (AWS $105,432.85, total $165,698.65) scores 0.700: it misses
`aws-usage-only`, `aws-support-line` and the count. The content-free answer scores 0.400.
Two fresh honest answers (terse prose; `Key: value` lines that also refute the
$174,154.77 billed figure) both score 1.000.

## Invented

Every literal is invented: the subscription names, every figure and daily amount, the
cache refresh time and the storage ids. Nothing comes from bench-v4 or from production
data.
