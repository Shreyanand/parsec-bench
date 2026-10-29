# bench-v5-cost-411-org-week-linked-account-league

## What it measures

A complete read of an org-wide `query_aws_costs` grouped by `LINKED_ACCOUNT`, with the
counting done right. The user wants a one-week league table of member accounts for
2026-08-17..2026-08-23. The instruction gives the exclusive query end 2026-08-24, so
there is no date trap. With no account filter and `LINKED_ACCOUNT` grouping, parsec
returns one `results` entry labelled `org-wide`. The accounts are the **keys of its
`items` map** (9 of them), stored in no particular order, and `accounts_queried` is 0. The
honest answer counts 9 accounts with spend and ranks them: 731904268155 $4,618.27,
647201958830 $3,388.91, 958316072648 $2,947.63. It counts 5 accounts over $1,000 (the
next is 519073846224 at $977.32, a near miss) and gives the $16,116.10 total. It is a
happy path, and its discrimination is completeness and arithmetic. An answer that takes
the first three keys in stored order, reports `accounts_queried` as the account count, or
skims the threshold gets the counts wrong.

## Grounding

- `api.json` AccountCost.account_id: "a LINKED_ACCOUNT-grouped query yields `org-wide`
  even when filtered". AwsCostResult.accounts_queried: "An empty account_ids list means an
  org-wide query, so this may be 0". AccountCost.items: "Keyed by the grouping dimension's
  value". DimensionCost carries `cost` plus a `daily` series. Every account's seven daily
  entries sum exactly to its `cost` (the generator asserts this).
- SKILL.md `/query_aws_costs POST`: `periods` resolves 2026-08-17/2026-08-24 to
  `per-aws-v8m-0824`. `aws_cost_results` is read by that `period_id` and returned exactly
  as stored. There is only one row for the period, so the selection is unambiguous.
  Derivation rule: `total_cost` equals the sum of returned `results[].total` (16,116.10).
- The `group_by` enum value `LINKED_ACCOUNT` is hit. The org-wide `AccountCost` row is
  mirrored in `account_costs`.

## Contract

- Expected call (unordered-subset): `query_aws_costs` with `account_ids: []`, 2026-08-17 to
  2026-08-24, `group_by: LINKED_ACCOUNT`. Every argument is in the instruction.
- `top-1`, `top-2` and `top-3` (required): the three account ids. `top-2` is fifth in
  stored order.
- Counts: `accounts-with-spend` 9 and `accounts-over-1000` 5 (both derived, with notes),
  and `org-total` $16,116.10.
- No forbidden facts. Weights 0.2/0.8, as the call is fully specified by the instruction.

## The wrong answer

"...the query covered 0 accounts queried, and the org total is $16,116.10. Top three
accounts: 731904268155 at $4,618.27, 260487913502 at $812.40 and 958316072648 at
$2,947.63. ... so 4 accounts went over $1,000." This answer reads the first keys in stored
order, misses 104829375561, and never counts the accounts. With the golden calls it scores
0.2 + 0.8 x 4/6 = 0.733 (`score_answer.py`). It keeps the total and all three id facts
(647201958830 is named in its over-$1,000 list), and misses both derived counts. The id
facts are weak on their own, because any full listing names all nine ids. The counts carry
the discrimination. The content-free answer scores 0.200.

## Invented

Every literal is invented: the nine account ids, every figure and daily amount, and the
storage ids. Nothing comes from bench-v4 or from production data.
