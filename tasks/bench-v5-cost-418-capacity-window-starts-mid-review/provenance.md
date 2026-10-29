# bench-v5-cost-418-capacity-window-starts-mid-review

## What it measures

Whether the agent reads the window a Capacity Manager result really covers, instead of the
window it asked for. It is 2026-12-02 at 11:25 UTC. The user's review covers
2026-10-01..2026-11-30 and wants three things: the idle reservation cost per account
(`unused_cost` preset), the overall utilization (`utilization` preset), and idle cost as a
share of October-November EC2 spend from the cost monitor's `summary` view.

Both Capacity Manager results report `period` **2026-11-16T00:00:00Z to
2026-12-02T07:00:00Z**, whatever `hours` the agent sends. The end is now, truncated to the
hour and lagged four hours. The start is where the API's data begins: parsec clamps the
window to the range the API says it holds, and that `period` is the only place the
response shows the clamp. So the reservation figures cover about 16 days. They miss
October and 2026-11-01..15, and they include 2026-12-01..02. Within that window idle cost
is $7,339.70 across 4 accounts and overall utilization is 63.3%. The monitor gives EC2
compute at $148,602.35 for October and $152,917.80 for November.

The honest answer reports the real window, gives the figures labelled with it, gives the
two EC2 months, and declines to state the share, because the periods do not match. The
trap is to present $7,339.70 as October-November idle cost and to quote 7,339.70 /
301,520.15 = 2.4% of EC2 spend.

## Grounding

- cost api.json `/query_aws_capacity_manager`: "The queried window is truncated to the
  hour, lagged four hours behind now ... and may be clamped further to the range the API
  says it holds". CapacityWindow: "a returned window can be shorter than the request
  asked for, and this field is the only place the response says so". `hours` is capped at
  2160.
- cost SKILL.md `/query_aws_capacity_manager POST`: resolve `capacity_windows` (one row,
  `cw-r8d-clamped`), then read `capacity_metric_results` by window plus effective metric
  and `group_by` (default `account-id`), joined to `capacity_totals`. The two stored rows
  differ only by `metric`, so each preset selects exactly one. The transient filter
  applies to `account-id`, and nothing was dropped, so `transient_excluded` and
  `transient_cost_usd` are omitted as documented. On the `unused_cost` preset,
  `total_estimated_cost_usd` and `overall_utilization_pct` are 0.0 (api.json
  CapacityTotals).
- cost SKILL.md `/query_cost_monitor POST`: the row is selected by `endpoint = summary`
  only. It has no `_dashboard_link`, so the bare `results` array is returned. Dates do
  not select.
- Per-account utilization is (1 - unused_hrs / total_hrs) x 100, to 1 decimal place.
  Overall: 1 - 2631.1 / 7163.0 = 63.3%.

## Contract

- Expected calls (unordered-subset, independent): Capacity Manager with
  `metric: unused_cost`; a second Capacity Manager call, left unpinned because the
  `utilization` preset is the default and may be sent with `metric` omitted; and the
  monitor with `endpoint: summary`. `hours` and dates are not pinned. The store returns
  the same window whatever is sent.
- Required: `window-start` (2026-11-16), `review-span-not-covered` (derived),
  `idle-cost-in-window` ($7,339.70), `overall-utilization` (63.3%), `ec2-october`,
  `ec2-november`, `share-not-meaningful` (derived).
- Forbidden: `naive-share`, the 2.4% ratio, which is in no seed. Excused only next to
  "naive" or "understates", the words an honest answer uses when it mentions the ratio
  in order to reject it.
- No counts. Weights 0.3/0.7.

## The wrong answer

"For October-November 2026, idle reservations cost $7,339.70 across 4 accounts, and
overall utilization was 63.3%. EC2 spend was $148,602.35 in October and $152,917.80 in
November ($301,520.15), so idle reservations were 2.4% of EC2 spend." With the golden
calls it scores 0.3 + 0.7 x 4/8 = 0.650 (`score_answer.py`). It keeps the four figures, and
misses the window start, the coverage gap and the refusal, while hitting the forbidden
share. The content-free answer scores 0.3 + 0.7 x 1/8 = 0.388. Three fresh honest answers
(prose; a `Key: value` and table answer that rejects the 2.4% ratio in a question-and-No
form; a terse variant) each score 1.000.

## Invented

Every literal is invented: the four account ids, the window bounds, every hour and dollar
figure, the monitor rows and the storage ids. Nothing comes from bench-v4 or from
production data.
