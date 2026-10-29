# bench-v5-cost-419-chargeback-predates-current-tenant

## What it measures

This is a three-service chain (cost, cloud, platform) for a chargeback. The inference is
that one month's bill on a reused sandbox account can span two tenancies, and only the
part after the current holder's provision is theirs. Finance's stated default is to bill
the whole month to whoever holds the account at month end.

1. `query_cost_monitor` `breakdown` (linked accounts, September 2026): the top row is
   `570284196633` (sandbox6217) at $13,548.63. The account id is not in the instruction.
2. `query_aws_costs` for that account, 2026-09-01..2026-10-01 (exclusive end stated). The
   daily series has two blocks. 2026-09-01..12 comes to $7,718.43 (about $640/day of EC2
   compute, tapering to $214.30 on 09-12). 2026-09-13..17 has no entries at all.
   2026-09-18..30 comes to $5,830.20 (about $455/day).
3. `query_aws_account_db` by `account_id`: holder `tnakashima`, GUID `w6hcx`, in use.
4. `query_aap2 find_jobs` with `template_name: w6hcx`: one job, provision 84152 on
   `west`, started 2026-09-18T14:51:07Z, successful.

The honest answer bills tnakashima $5,830.20, from the provision day to month end. It says
the $7,718.43 before the gap predates their lab and belongs to an earlier use of the
account, which these tools cannot name. The trap is to apply the default and bill
tnakashima the full $13,548.63.

## Grounding

- cost SKILL.md `/query_cost_monitor POST`: the row is selected by `endpoint = breakdown`
  only. With no `_dashboard_link`, the bare `results` array is returned. Rows use the
  linked-account shape of the existing v5 breakdown seeds.
- cost SKILL.md `/query_aws_costs POST`: `periods` resolves 2026-09-01/2026-10-01 to
  `per-aws-h7c-2609`. The row is returned as stored. api.json AccountCost.account_id: an
  account filter with SERVICE grouping yields two keys, hence the 12-digit id.
  DimensionCost `{cost, daily}`. Days with no charge carry no daily entry, as Cost
  Explorer returns no group for them. Each item's `cost` equals the sum of its daily
  entries. `accounts_queried` is 1 (one returned entry).
- cloud SKILL.md `/query_aws_account_db POST`: with no `name`, a collection scan with an
  exact `account_id` filter. Rows are returned minus `sandbox_account_id` in
  `{accounts, count, truncated}`. Two decoy rows are filtered out.
- platform SKILL.md `query_aap2 find_jobs`: `template_name` matches the stored `job_name`
  as a case-insensitive substring, ordered by `finished` descending, projected to the
  JobSummary fields, with `total` = `len(jobs)`. The decoy job for `k9prm` does not match.

## Contract

- Expected calls (ordered-subsequence, the order the instruction lists): `breakdown`,
  then Cost Explorer for the discovered account, then the account DB by that
  `account_id`, then `find_jobs` with the GUID from the DB (`w6hcx`, which is not in the
  instruction). The breakdown's `group_by` is left unpinned.
- Required: `top-account`, `current-holder`, `provisioned-date` (2026-09-18),
  `not-billable-amount` ($7,718.43, derived) and `earlier-spend-predates-lab` (derived).
- Count: `billable-amount` $5,830.20 (derived, with a note).
- Forbidden: `whole-month-to-holder`, claims that bill tnakashima for the full month.
  Excused only by phrases that attribute the claim to the default rule ("default rule
  would", "month-end rule would").
- Weights 0.25/0.75, per the slot.

## The wrong answer

"The top account is 570284196633 (sandbox6217), $13,548.63 for September. It's held by
tnakashima (lab w6hcx, provisioned 2026-09-18 by job 84152). Under the month-end rule,
bill the whole month to tnakashima: $13,548.63, and nothing needs to be held back." With
the golden calls it scores 0.25 + 0.75 x 3/7 = 0.571 (`score_answer.py`). It keeps the
account, the holder and the date, misses both derived facts and the billable count, and
hits the forbidden claim. The content-free answer scores 0.25 + 0.75 x 1/7 = 0.357.

## Invented

Every literal is invented: the account ids, sandbox names, GUIDs, people, job ids, hosted
zones and service UUIDs, every figure and daily amount, and the storage ids. Nothing comes
from bench-v4 or from production data.
