# bench-v5-cost-416-peak-day-is-a-cross-service-sum

## What it measures

Whether the agent builds an account's daily totals from per-service daily series, instead
of reading the single largest daily line as the peak day. A spend-anomaly alert flagged
AWS account `529364071846` for 2026-09-14..2026-09-20. The instruction states the
exclusive query end 2026-09-21, so there is no date trap. `query_aws_costs` (SERVICE)
returns four services, each with a seven-day `daily` series. The biggest single number in
the response is EC2 compute's $2,960.15 on 2026-09-15. But the account's highest **total**
day is 2026-09-18, at $4,309.05. On that day AWS Data Transfer ($1,688.35) and Amazon S3
($1,366.20) spike roughly tenfold while EC2 stays at its usual ~$1,200. The 2026-09-15 total
is $3,316.55. Two days exceed $2,000. The honest answer gives 2026-09-18, $4,309.05, data
transfer and S3 as drivers, and 2 days. The trap is to answer "2026-09-15, driven by EC2,
the only day over $2,000".

## Grounding

- SKILL.md `/query_aws_costs POST`: `periods` resolves 2026-09-14/2026-09-21 to
  `per-aws-w7q-0921`, and the `aws_cost_results` row for that `period_id` is returned
  exactly as stored. The `AccountCost` row is mirrored in `account_costs`.
- `api.json` AccountCost.account_id: an account filter with SERVICE grouping gives two
  Cost Explorer keys, so the entry carries the 12-digit id, not `org-wide`.
  AccountCost.items: "Keyed by the grouping dimension's value". DimensionCost: `cost` plus a
  `daily` series of DailyCost `{date, cost}`.
- Every service's `cost` equals the sum of its seven daily entries. The account `total` and
  `total_cost` ($15,391.05) equal the sum of the four. The generator asserts the peak-day
  sum ($4,309.05) and the count of days over $2,000 (2).
- `accounts_queried` is 1, the number of returned entries (SKILL.md Derivation Rules). It
  agrees with api.json here.

## Contract

- Expected call (unordered-subset): `query_aws_costs` with
  `account_ids: ["529364071846"]` and `start_date: 2026-09-14`. The end date is unpinned;
  the instruction states it.
- `peak-date` (required): 2026-09-18, in date notations.
- `driver-transfer` and `driver-s3` (required): the two services that spike on the peak
  day. A full service listing earns these on any reading (bar C).
- Counts: `peak-day-total` $4,309.05 (derived, with a note) and `days-over-2000` 2 days
  (derived, with a note). The EC2-only reading gives one day.
- Forbidden `biggest-line-day-as-peak`: 2026-09-15 (in date notations) asserted as the peak,
  highest-spend, most expensive or biggest day. It is excused in a sentence that qualifies
  it as EC2's own peak, the second-highest day or the largest single line. No required form
  contains an excuse.
- Weights 0.2/0.8.

## The wrong answer

"The peak day was 2026-09-15, when EC2 compute hit $2,960.15 ... That EC2 spike drove the
anomaly. It was the only day over $2,000" plus a correct week total and per-service totals.
With the golden calls it scores 0.2 + 0.8 x 2/6 = 0.467 (`score_answer.py`). It earns the
S3 and data-transfer facts only through its service list, and misses the date, both counts
and the forbidden fact. A fabricator that states the 2026-09-15 cross-service total as the
peak, but mentions the 18th, scores 0.600 (bar C: true literals plus a false claim). Two
fresh honest answers score 1.000. One is terse prose. The other uses `Key: value` lines and
an explicit "Was 2026-09-15 the peak? No." Gate floors: mute 0.333, nocall 0.133,
fabricate 0.200.

## Invented

Every literal is invented: the account id, every daily figure and the storage ids. Nothing
comes from bench-v4 or from production data.
