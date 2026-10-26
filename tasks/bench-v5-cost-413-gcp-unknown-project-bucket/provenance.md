# bench-v5-cost-413-gcp-unknown-project-bucket

## What it measures

Whether the agent recognises a tool's sentinel label in a breakdown and does not treat it
as a real entity. The user re-bills GCP spend to the team that owns each project, and asks
for July 2026 (2026-07-01..2026-07-31) by project: each project's cost, how many projects
to re-bill, and whether the re-bills add up to the total. `query_gcp_costs`
(`group_by: PROJECT`) returns six breakdown lines. One of them, the second largest at
$6,412.30, is named **`unknown`**. That is parsec's literal for billing rows whose project
field is null or empty. The honest answer lists the five real projects, says there are 5
to re-bill, and says `unknown` is not a project. The re-bills ($25,297.48) therefore fall
$6,412.30 short of the $31,709.78 total, and that amount cannot be attributed to a team
from this data. The trap is to count six projects and promise re-bills that cover the
whole bill.

## Grounding

- `api.json` GcpCostResult.breakdown[].name: "The GCP service name or project id, per
  group_by -- or the literal string `unknown` when the row's own field is null or empty
  (src/tools/gcp_costs.py:106-109)". breakdown is "sorted by cost descending", and the seed
  is stored in that order.
- SKILL.md `/query_gcp_costs POST`: `periods` resolves 2026-07-01/2026-07-31 to
  `per-gcp-h6t-0731`. Then `gcp_cost_results` is read by `period_id` and `group_by`
  (PROJECT), and the inline breakdown is returned verbatim, with `total_cost` as stored.
  A SERVICE row for the same period is also seeded, with the same total and no `unknown`
  line, so an agent that first omits `group_by` gets a real answer rather than a
  not-found error. The `group_by` enum values `PROJECT` and `SERVICE` are hit.
- The six PROJECT lines and the six SERVICE lines each sum to 31,709.78 (the generator
  asserts this).

## Contract

- Expected call (unordered-subset): `query_gcp_costs` 2026-07-01 to 2026-07-31 with
  `group_by: PROJECT` (structural, from "grouped by project").
- `unknown-is-not-a-project` (required, derived): `unknown` is not a project, has no
  project id, or cannot be attributed or billed.
- `top-project` (required): ml-feature-store-prod, so the list is actually reported.
- Counts: `billable-projects` 5 (derived, with a note), `unattributed-amount` $6,412.30 and
  `month-total` $31,709.78.
- `unknown-billed-as-project` (forbidden): "6 projects to re-bill", "owner of the unknown
  project", "the re-bills will add up to the full ...", "every dollar is assigned" and
  similar asserting forms. A denied occurrence ("not every dollar is assigned", "won't add
  up") is excused by polarity. No `attributed_to`.
- Weights 0.3/0.7.

## The wrong answer

The answer lists all six lines, including "unknown $6,412.30", with the total, then says:
"That's 6 projects to re-bill, and the re-bills will add up to the full $31,709.78." With
the golden calls this scores 0.3 + 0.7 x 3/6 = 0.65 (`score_answer.py`). It keeps
`top-project` and both money counts, misses `unknown-is-not-a-project` and
`billable-projects`, and hits the forbidden fact. The content-free answer scores 0.417.

## Invented

Every literal is invented: the project ids, all figures, the row count and the storage
ids. The service names are real GCP product names, chosen so that none appears in a
bench-v4 seed. Nothing comes from bench-v4 or from production data.
