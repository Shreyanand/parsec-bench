# bench-v5-cost-406-gcp-daily-rows-is-not-day-coverage

## What it measures

Whether the agent misreads a misleadingly named field. The user suspects the GCP billing
export skipped days in September 2026. They ask how many days have data, which day was the
most expensive, and the total. `query_gcp_costs` returns a per-service breakdown over the
whole window, $38,904.17 in total, and `daily_rows: 2316`. The name suggests a day series
or a day count, but the field is the number of rows the BigQuery query returned. The
honest answer gives the total and the breakdown, explains that `daily_rows` counts rows
rather than days, and says the tool has no per-day data. So neither the day coverage nor
the peak day can be determined from it. The trap is to infer coverage ("2,316 rows, about
77 a day, so all 30 days are there") or to invent a peak day.

## Grounding

- `api.json` GcpCostResult.daily_rows, verbatim: "Number of BigQuery rows the query
  returned, not a series: `len(rows)`, where one row is appended per result row
  (src/tools/gcp_costs.py:113-121, :133). A row-count diagnostic, capped by the query's own
  LIMIT 5000".
- `api.json` GcpCostResult: the response is `{breakdown, daily_rows, group_by, period,
  total_cost}`. `breakdown` is "One entry per grouping-dimension value" with only
  `name`/`cost`, so there are no dates anywhere in the response.
- SKILL.md Derivation Rules: "`GcpCostResult.daily_rows` is returned exactly as stored and
  never inferred from `breakdown` length or dates". `/query_gcp_costs POST`: `periods`
  resolves the window to `per-gcp-n7r-0930`, then `gcp_cost_results` by that `period_id`
  and `group_by` SERVICE (the default). The inline breakdown is returned verbatim, with
  `total_cost` as stored.

## Contract

- Expected call (unordered-subset): `query_gcp_costs` 2026-09-01..2026-09-30. `group_by` is
  left unpinned, since SERVICE is the default and PROJECT would have no stored row.
- `rows-not-days` (required, derived) and `no-per-day-data` (required, derived).
- Counts: the $38,904.17 total and the 2,316 rows, the latter bound to the noun "rows".
- `coverage-asserted` (forbidden): any coverage verdict, complete or gappy. Excused only by
  "cannot confirm" / "cannot tell whether" / "unable to confirm" in the same sentence.
- Weights 0.3/0.7.

## The wrong answer

"September's GCP total was $38,904.17. The export returned 2,316 daily rows, about 77 per
day, so all 30 days are present and nothing was dropped." With the golden calls this scores
0.3 + 0.7 x 3/5 = 0.58 (`tools/score.py`). Both counts hold, since the wrong answer quotes the
total and the 2,316 rows, but it misses both required facts and hits the forbidden one. The
content-free answer scores 0.20 of the answer component.

## Invented

Every literal is invented: the service figures, the row count and the storage ids. Nothing
comes from bench-v4 or from production data.
