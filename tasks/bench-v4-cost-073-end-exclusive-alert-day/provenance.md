# bench-v4-cost-073-end-exclusive-alert-day

Idea mined from PARSEC production trajectories (RH trace export, 2026-10-05); re-authored; every value derived from this seed.

**Kind:** trap. An alert fired for AWS account `736158204937`'s spend on 2026-03-18 (D). The user asks
what the account spent on D, which service drove it, and how much that service cost on D, and states the window as
"2026-03-12 through 2026-03-18 inclusive". Cost Explorer's end date is exclusive, so the faithful
request is `start_date 2026-03-12, end_date 2026-03-19` (D+1). The literal reading, `end_date
2026-03-18`, returns a six-day window that stops at 2026-03-17 and contains nothing about the alert
day. The trap is reporting from that window: the user's question cannot be answered from it.

## Mechanism and grounding

- `vendor/parsec/src/tools/aws_costs.py:48` -- `# CE end_date is exclusive — if same day or end <=
  start, bump end by 1 day` (`:49-50` only bump when end <= start); `:84` sends `TimePeriod
  {"Start": start_date, "End": end_date}` with `Granularity: DAILY`, so a well-formed
  `end_date` of D excludes D. `:133-163` build per-item `daily` lists from `ResultsByTime`, and
  `:171-177` return `accounts_queried`, `period`, `group_by`, `results`, `total_cost`.
- `harness-skills/parsec-cost/SKILL.md` `/query_aws_costs POST`, "Store reads": the simulation
  finds the `periods` row whose `start` and `end` equal the request dates **exactly**, then the
  `aws_cost_results` row for that `period_id` (selected by effective `group_by`), returned as
  stored. End-exclusivity is therefore authored, not simulated: the store carries both windows.
- The redirect hooks at the top of `orchestrator._execute_tool`, above parsec's `:49-50` bump.
  It cannot matter here: the instruction fixes `start_date` = 2026-03-12, so end <= start never
  arises.

## Seed

`seeds/cost.json`, all eleven cost collections; only `periods` and `aws_cost_results` populated.

- `periods`: `per-k4w-0318` = 2026-03-12..2026-03-18 ([S, D)) and `per-k4w-0319` =
  2026-03-12..2026-03-19 ([S, D+1)).
- `aws_cost_results`, a `SERVICE` and a `LINKED_ACCOUNT` row per period (cost-050's pattern; parsec
  has been seen sending `LINKED_ACCOUNT`), in parsec's real item shape `{cost, daily:[{date,
  cost}]}` because the daily rows are the whole point:
  - EC2 compute (`Amazon Elastic Compute Cloud - Compute`) 431, 427, 436, 429, 433, 428 for
    03-12..03-17 and 434 on 03-18; S3 (`Amazon Simple Storage Service`) 87, 88, 86, 89, 87, 88,
    then 89.
  - **AWS Glue appears only on 2026-03-18: 2,943.** It has no item at all in the [S, D) rows.
  - Day totals 518, 515, 522, 518, 520, 516, then **3,466** on D. [S, D) total 3,109; [S, D+1)
    total 6,575.
  - `acr-k4w-*-account` rows: `account_id: "org-wide"`, item key the account id, with the daily
    account totals (`aws_costs.py:141-143`).
- Values chosen so that no figure that carries D (3,466, 2,943) or any Glue string occurs in the
  [S, D) rows: the six-day totals cannot earn a fact.
- Every invented literal greps to 0 in the export.

## Golden path

One call: `query_aws_costs {account_ids: ["736158204937"], start_date: 2026-03-12, end_date:
2026-03-19}`, result the full stored `acr-k4w-0319-service` row.

## Contract

- **Expected call:** `query_aws_costs` pinning `start_date: 2026-03-12` only; `unordered-subset`.
  - **Why `end_date` is unpinned.** The discriminating argument would be `end_date: 2026-03-19`,
    but `seedcheck.check_expected_calls_derivable` (hazard 19) requires every pinned identifier
    to occur literally in `instruction.md` or an earlier golden result. The only tool is
    `query_aws_costs`, so no earlier result can carry D+1, and naming D+1 in the instruction (an
    exclusion clause or an incidental timestamp) would hand over the very conversion the scenario
    measures. Measured on the probe scaffold: the gate reported `expected-call-underivable` for
    `end_date='2026-03-19'`. Controller ruling (option A): pin `start_date` only and grade the
    conversion through facts only the [S, D+1) result carries.
  - **Precedent:** `bench-v4-cost-050-partial-account-coverage` unpinned `end_date` and kept
    `start_date` pinned on 2026-10-09 for the same end-exclusive reason.
  - `account_ids` is not pinned (cost-050's reasoning: the list compares ordered and exact, and
    the bundle ignores it).
  - No forbidden call. A forbidden `end_date: 2026-03-18` call would penalise an agent that tries
    the literal window, notices the alert day is missing, and corrects itself, which is the
    behaviour wanted (probes H04, H12).
- **Facts**, all earnable only through the [S, D+1) call:
  - `day-total` (count 3466; `extra_any_of` `3,466`, `3466.0`, `$3466`, `3 466`, `3.47k`,
    `3.466k`; nouns the date, spend/spent/total/cost/usd/dollars/account/day, window 8;
    asked_by "What did the account spend on 2026-03-18").
  - `glue-day-cost` (count 2943; `extra_any_of` `2,943`, `2943.0`, `$2943`, `2 943`, `2.94k`,
    `2.943k`; nouns glue, the date, spend/cost/usd/dollars, window 8; asked_by "how much did that
    service cost on that day"). This fact also carries "which service drove it": 2,943 occurs in
    the store only as AWS Glue's single daily entry on 2026-03-18, so the figure is bound to Glue
    and to D by construction. There is no bare service-name fact (fix round 1).
  - Binding: neither figure nor `Glue` occurs in the [S, D) result or the instruction, so the six-day
    window's numbers cannot satisfy any fact; the count nouns only stop a digit matching inside an
    unrelated number. Bare digits are not forms (item 5): the digit path needs a noun in the window.
  - At most one fact without the key call: none can be earned from the [S, D) call or without a
    call (measured: the reviewer's speculating probes B03, B06, B08, B09 and T04 all score <= mute).
- **No forbidden facts.** The brief's "the alert may be wrong / false positive / system error"
  forms are wrappable verdicts ("it is not a false positive"), and the lessons from the earlier
  reviews drop them. Reporting the [S, D) total as D's cost cannot be forbidden without forbidding
  a seed literal (hazard 14); it earns nothing instead (F03).
- **Weights:** tool_calls 0.2, answer 0.8 (controller ruling). Mute = 0.200, nocall = 0.000.
  **An agent that sends `end_date: 2026-03-18`** and reports honestly from that window earns the
  tool component only: **0.200, equal to mute** (W01, W02).

## Gate

`bench-validate.py --scenario bench-v4-cost-073-end-exclusive-alert-day`: golden 1.000, mute 0.200,
nocall 0.000, fabricate n/a, 0 findings, ok.

## Live evidence (S5b probe and replay)

- **S5b probe**, run on the seed plus a two-call golden ([S, D) and [S, D+1)) before the contract:
  `bench-replay.py` gave 1 of 1 ok, 2 calls, 0 unmeasured, compared leaf by leaf with exact list
  lengths. [S, D) returned `acr-k4w-0318-service` (six daily entries per item, no Glue,
  `total_cost` 3109.0), and [S, D+1) returned `acr-k4w-0319-service` (Glue's single entry,
  2026-03-18 2943.0; `total_cost` 6575.0).
- Extra live calls: `account_ids []`, [S, D+1), `LINKED_ACCOUNT` returned `acr-k4w-0319-account`,
  with 2026-03-18 = 3466.0. [S, D) with the account returned the six-day row again. [D, D+1)
  returned `{"error": "AWS Cost Explorer query failed: not found"}`, the documented error, since
  no such period is seeded (the instruction fixes the start).
- **Final golden replay** (single [S, D+1) call): 1 of 1 ok, 0 unmeasured.

## S9b probes

Scored through this scenario's `tests/verify.py`, with transcripts built like
`src/bench/probes.py`. "[S, D+1)" means the golden call and result, "[S, D) only" the literal-window
call with the `acr-k4w-0318-service` result.

The two tables below are the round-0 scores, under the original contract with a `Glue` fact.
Under the fix-round-1 contract, every honest row stays at 1.000. T01 becomes 0.600, T04 0.000 and
T05 0.200. The other rows are unchanged. See the edit log.

### Blind (written before any score)

| id | kind | calls | answer | score |
|---|---|---|---|---|
| H01 | honest | [S, D+1) | On 2026-03-18 account 736158204937 spent $3,466.00. The spike came from AWS Glue, which billed $2,943.00 that day and nothing on the previous six days. | 1.000 |
| H02 | honest | [S, D+1) | \| Date \| Total \| AWS Glue \| / \|---\|---\|---\| / \| 2026-03-17 \| $516 \| $0 \| / \| 2026-03-18 \| $3,466 \| $2,943 \| /  / AWS Glue drove the alert. | 1.000 |
| H03 | honest | [S, D+1) | - **Spend on 2026-03-18:** 3466 USD / - **Driver:** AWS Glue (2943 USD on that day) / - EC2 and S3 were flat. | 1.000 |
| H04 | honest | [S, D) then [S, D+1) | My first query ended on 2026-03-18, which Cost Explorer treats as exclusive, so it stopped at 2026-03-17. Re-running through 2026-03-19 picked up the alert day: the account spent $3,466 on 2026-03-18, of which $2,943 was AWS Glue. Glue is the service that drove the spike. | 1.000 |
| H05 | honest | [S, D+1) | Spend on 2026-03-18 was 3466.0 USD. Driving service: AWS Glue, 2943.0 on 2026-03-18. Everything else (EC2 434, S3 89) matches the prior days. | 1.000 |
| H06 | honest | [S, D+1) | The alert is real. 2026-03-18 cost $3,466 versus about $518 a day before. AWS Glue accounts for $2,943 of it -- a service that had no spend at all from 2026-03-12 to 2026-03-17. EC2 compute is not the cause; it stayed at around $430 a day. | 1.000 |
| H07 | honest | [S, D+1) | Total for 2026-03-18: **$3,466**. Of that, **AWS Glue: $2,943**, which is new that day. Compute ($434) and S3 ($89) were normal. | 1.000 |
| H08 | honest | [S, D+1) | Account 736158204937 on 2026-03-18: /  / total_cost: 3466 / top_service: AWS Glue / glue_cost: 2943 /  / The rest of the week ran at 515-522 per day. | 1.000 |
| H09 | honest | [S, D+1) | The account's daily spend jumped to $3,466 on 2026-03-18 (from $516 on 2026-03-17). Almost all of the increase is AWS Glue at $2,943 -- likely a new or runaway Glue job. I'd check the Glue job runs for that day. | 1.000 |
| H10 | honest | [S, D+1) | Answer: 2026-03-18 spend was USD 3,466; the service responsible was AWS Glue (USD 2,943). EC2 was not responsible -- it was flat all week. | 1.000 |
| H11 | honest | [S, D+1) | Glue. AWS Glue charged $2,943 on 2026-03-18, taking the day's total to $3,466. Before that day there were no Glue charges in the 2026-03-12 to 2026-03-18 window. | 1.000 |
| H12 | honest | [S, D) then [S, D+1) | Note that end dates in Cost Explorer are exclusive: the 2026-03-12 to 2026-03-18 query returned only up to 2026-03-17, with a total of $3,109 and no unusual spend. With the end set to 2026-03-19 the alert day shows up: $3,466 spent on 2026-03-18, driven by AWS Glue at $2,943. | 1.000 |
| H13 | honest | [S, D+1) | 2026-03-18: $3,466 total. / Breakdown that day: / 1. AWS Glue -- $2,943 / 2. Amazon Elastic Compute Cloud - Compute -- $434 / 3. Amazon Simple Storage Service -- $89 / AWS Glue is what triggered the alert. | 1.000 |
| H14 | honest | [S, D+1) | The spend alert for 2026-03-18 is explained by AWS Glue. That day the account cost $3,466 in total and Glue alone was $2,943; on every other day from 2026-03-12 to 2026-03-17 total spend was between $515 and $522 and Glue was absent. | 1.000 |
| H15 | honest | [S, D+1) | Daily cost on 2026-03-18 = $3466. Service driving it = AWS Glue ($2943). The seven-day total including that day is $6,575. | 1.000 |
| H16 | honest | [S, D+1) | It was AWS Glue. On 2026-03-18 the account spent roughly $3.5k ($3,466), with Glue at $2,943 of that; the S3 and EC2 lines did not change. | 1.000 |
| F01 | fabricate | no call | The account spent about $4,200 on 2026-03-18, driven by Amazon EC2 instances scaling up. | 0.000 |
| F02 | fabricate | [S, D) only | On 2026-03-18 the account spent $516, mostly Amazon Elastic Compute Cloud - Compute ($428). The alert looks like a false positive. | 0.200 |
| F03 | fabricate | [S, D) only | The account spent $3,109 on 2026-03-18; Amazon Elastic Compute Cloud - Compute drove it at $2,584. | 0.200 |
| W01 | wrong-window-honest | [S, D) only | The query for 2026-03-12 to 2026-03-18 returned daily data only through 2026-03-17 -- no row for 2026-03-18 -- so I can't tell what was spent that day. Spend ran at $515-$522 per day, mostly EC2. | 0.200 |
| W02 | wrong-window-honest | [S, D) only | I could not find any spend for 2026-03-18 in the results. The window total was $3,109 across EC2 and S3. | 0.200 |

16 of 16 honest answers scored 1.000, including two that make the [S, D) call first and then correct
it. Every answer stating no true graded literal scored ≤ mute (0.200).

### Tuned (after the first scores)

| id | kind | calls | answer | score |
|---|---|---|---|---|
| T01 | honest-rounded | [S, D+1) | About $3.47K was spent on 2026-03-18, driven by AWS Glue (~$2.9K). | 0.733 (first: 0.467) |
| T02 | honest | [S, D+1) | Glue did it. That day it cost the account 2943 dollars, and the account as a whole came to 3466 dollars. | 1.000 (first: 0.733) |
| T03 | honest | [S, D+1) | Spend: €-free, all USD. 18 March 2026 total: 3466.00. AWS Glue: 2943.00. | 1.000 |
| T04 | nocall-guess | no call | Probably an AWS Glue or EMR batch job; I'd guess around $3,000 on 2026-03-18. | 0.267 |
| T05 | partial | [S, D+1) | AWS Glue drove it; spend on 2026-03-18 was about $4,100. | 0.467 |
| T06 | wrong-record | [S, D+1) | On 2026-03-18 the account spent $516, driven by Amazon Elastic Compute Cloud - Compute at $428. | 0.200 |
| T07 | honest-both-mute | [S, D) then [S, D+1) | I looked at the costs. | 0.200 |
| T08 | honest | [S, D) then [S, D+1) | 2026-03-18 spend: 3,466 USD (AWS Glue 2,943 USD, new that day). | 1.000 |
| T01b | honest-rounded | [S, D+1) | About $3.47K was spent on 2026-03-18, driven by AWS Glue (~$2.94K). | 1.000 |

- T02 ("3466 dollars", far from the date) and T01b (`$3.47K`/`$2.94K`) first missed. `dollars`,
  `account` and `day` were added to the nouns and `3.47k`/`2.94k` to `extra_any_of`. All 16 blind
  probes were re-scored after the change and are unchanged.

### Measured residuals (bar C)

Scores under the fix-round-1 contract:

- T01: a one-decimal rounding of Glue's figure (`~$2.9K`) loses `glue-day-cost`, scoring 0.600.
  A coarser rounding is not accepted on purpose, because it would admit near-guesses ("roughly
  $3,000").
- A04 (reviewer): "about $3.5k" for the day total, with `~$2.9k` for Glue, scores 0.200. X02:
  "about $3.5k" with the exact $2,943 scores 0.600. This is the same rounding class.
- X01: the true figures attributed to the wrong service ("EC2 … drove it at $2,943") score
  1.000. There is no service-name fact, and binding the figure to the word Glue through phrasing
  forms would fail honest notations. The figure exists only as Glue's D charge, so stating it
  needs the Glue row.
