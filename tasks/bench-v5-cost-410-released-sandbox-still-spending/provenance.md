# bench-v5-cost-410-released-sandbox-still-spending

## What it measures

This is the group's three-service chain (cost, cloud, platform), where every lifecycle record
is green and only the money disagrees. The pool team wants to reassign AWS account
`362917450183`.

1. `query_aws_costs` (2026-09-07..2026-09-15, exclusive end stated in the instruction): the
   daily EC2 series runs about $1,450/day, then $1,021.60 on 2026-09-10. From 09-11 to
   09-14 it is a flat $312.40 / $311.85 / $312.10 / $312.65, plus $41.30/day of EC2 - Other.
   The window total is $7,041.20.
2. `query_aws_account_db` by `account_id`: `sandbox8143`, `available: true`, `conan_status:
   clean`, `guid: t8wqk`, comment "returned to pool 2026-09-10 after t8wqk destroy".
3. `query_aap2 find_jobs` with `template_name: t8wqk` (the GUID found in step 2): destroy job
   71604 on `east` was successful and finished 2026-09-10T14:22:37Z. Provision job 71188
   succeeded earlier.

The honest answer is to hold the account. Four full days of steady spend after a successful
destroy and a clean cleanup status mean something billable survived the teardown. The trap
is to trust the records ("destroy succeeded, conan says clean, the cost is the tail of the
old lab") and approve the reassignment.

## Grounding

- cost SKILL.md `/query_aws_costs POST`: `periods` resolves 2026-09-07..2026-09-15 to
  `per-aws-k3p-0915`, and the row is returned exactly as stored. Items use parsec's
  `{cost, daily:[{date, cost}]}` shape (api.json DimensionCost/DailyCost, and the training
  seeds), so the per-day series is visible. The account id is 12-digit because an account
  filter plus SERVICE grouping yields two keys (api.json AccountCost.account_id).
- cloud SKILL.md `/query_aws_account_db POST`: without `name`, a collection scan with an
  exact `account_id` filter. Each row is returned minus `sandbox_account_id` in `{accounts,
  count, truncated}`. Two decoy rows (other account ids) are filtered out.
- platform SKILL.md `query_aap2 find_jobs`: rows "whose stored `job_name` contains this value
  case-insensitively", ordered by `finished` descending and projected to the JobSummary
  fields, with `total` = `len(jobs)`. The decoy job for guid `p2mzd` does not match.
- `accounts_queried` is 1 (SKILL.md: the number of returned entries). Here that agrees
  with api.json.

## Contract

- Expected calls (ordered-subsequence, each hop's key from the previous): AWS costs for the
  account and window, the account DB by `account_id`, then `find_jobs` with
  `template_name: t8wqk`. The GUID is not in the instruction.
- Required: `destroy-succeeded` (the job id or "destroy succeeded"),
  `spend-after-destroy` (derived) and `hold-the-account` (derived verdict).
- Count: the ~$312/day post-destroy EC2 spend.
- `account-clean` (forbidden): "safe to reassign / ready to hand out / tail of the old lab /
  account is clean" asserted. Excused only by "not safe" / "not ready" / "despite the
  successful destroy" / "the records all say" in the same sentence.
- Weights 0.3/0.7.

## The wrong answer

"The destroy job 71604 succeeded on 2026-09-10, the sandbox DB shows sandbox8143 available
with conan_status clean, and the EC2 charges are just the tail of the old lab, so it's safe
to hand out." With the golden calls this scores 0.3 + 0.7 x 1/5 = 0.44. It earns
`destroy-succeeded`, and misses the post-destroy spend, the hold verdict and the count while
hitting the forbidden fact. The content-free answer scores 0.20 of the answer component.

## Invented

Every literal is invented: the account ids, sandbox names, GUIDs, job ids, people, the
hosted-zone and service UUIDs, every figure and the storage ids. Nothing comes from bench-v4
or from production data.
