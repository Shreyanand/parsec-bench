# bench-v5-platform-115-find-jobs-default-page-not-the-total

## What it measures

Whether the agent treats a `find_jobs` `total` as a corpus count. 57 jobs on controller
`partner0` failed in September 2026. A `find_jobs` call with the right filters but the
default `max_results` returns exactly 50 rows with `total: 50`. Nothing in the envelope says
the page was cut, but the tool's own schema does: `max_results` has `default: 50`, and
`total` is "the length of `jobs` after `max_results` is applied, so it is a page count, not a
corpus count" (api.json `/query_aap2`; SKILL.md lines 166 and 282). A `total` that equals the
default page size is the signal. The instruction says the figure is audited and must cover
"every failed job in the month, not a sample or a first batch", which justifies re-querying
with a larger `max_results` (anything from 57 to 200).

The second ask makes the cut cost more than one number. `find_jobs` orders by `finished`
descending, so the page drops the seven *earliest* failures (1-4 September). Four of those
belong to `retail-pos-edge-lab`. On the page, `fintech-api-gateway-lab` leads 18-15. Over the
month, `retail-pos-edge-lab` leads 19-18.

**Kind: trap.** Reporting the first page as the month.

## Grounding

- `query_aap2` `find_jobs` (platform SKILL.md "/query_aap2 POST", Store reads "For
  `find_jobs`"): reads `jobs`, keeps rows by exact `controller` and `status`, keeps rows whose
  `started` is strictly between the date bounds (date-only bound = midnight UTC), orders by
  `finished` descending, then applies `max_results` (default 50, clamp 200). `total` =
  `jobs.length` after the cut.
- Enums: controller `partner0`; status `failed`.
- Seed: 57 target rows (partner0, failed, started 2026-09-01T03:17Z .. 2026-09-29), plus
  decoys that each filter excludes: 5 partner0 failures in August/October (latest August
  start 2026-08-28, so `created_after: 2026-08-31` still gives 57), 5 partner0 successes in
  September, and 3 east failures in September. Every `job_id` and `guid` is unique.
- Golden calls: the default call (50 rows, `total: 50`), then the same filters with
  `max_results: 200` (57 rows). Both results are computed by `ops_lib.find_jobs` from the seed.
  validate.py WARNs that the values 50 and 57 are "not in seeds". They are the derived `total`
  (length of the returned list), so the WARNs are justified.

## Contract

- tool_calls (0.3): one expected `find_jobs` with `controller: partner0`, `status: failed`.
  Dates and `max_results` are unpinned: a call with a larger page and the right filters scores
  the same as one that pages after seeing 50. The page cut is graded in the answer.
- answer (0.7):
  - count `failed-total` = 57 (nouns failed/failures/jobs, window 5).
  - count `top-count` = 19, and required `top-template` = retail-pos-edge-lab.
  - forbidden `fifty-is-the-month`: "50 failed" / "50 failures" / "50 jobs failed".
    attributed_to is limited to phrases that name the page: "first page", "only the first 50",
    "default page", "page of 50", "default max_results", "capped at 50", "cut at 50",
    "first call", "page cut". An honest answer can say "the first page showed 50 failed jobs".
  - forbidden `page-top-template`: the page-only winner stated as the month's top template.
    Same excuses, plus "looked like".
- Probe: "The controller shows 50 failed jobs rather than more, and fintech-api-gateway-lab
  was the worst, not retail." scores answer 0.0. Both forbidden facts hit, because "rather
  than" and "not" are not excuses.

## The wrong answer

"Controller partner0 had 50 failed jobs in September 2026. By template:
...fintech-api-gateway-lab.prod-provision had the most with 18 failures, then
retail-pos-edge-lab with 15..." scores reward **0.44**: both counts missed and both forbidden
facts hit. The golden answer scores 1.0. Mute floor (validate.py): answer 0.40, reward 0.58 with golden calls; above the 0.50 cap, and exempt (see `## Floor exemption`).

## Invented

Every literal is invented: job ids 8830101-8830403, the GUIDs, the four `partner_ext.*`
catalog items and their template names, and all timestamps. Nothing comes from bench-v4 or
from production data.

## Floor exemption

Weak discriminator, flagged in the baseline report (controller ruling 2026-10-13, in place of the owner-approved breakdown counts; flagged to the owner): the contract grades three required facts (counts failed-total and top-count, required top-template) and two forbidden facts at weights 0.3/0.7, so an agent that makes the golden calls and asserts nothing keeps the two forbidden facts and collects 0.3 + 0.7 x 2/5 = 0.580 (mute), and one that makes no call collects 0.280 (nocall), above the 0.50 / 0.25 caps; the fabricate probe scores 0.300 (max 0.440, below mute). A reweight to 0.25/0.75 alone gives 0.550 / 0.300 and still fails. The owner-approved counts for the asked 'one-line breakdown per template' (fintech-count 18, telco-count 12, claims-count 8) were tried (d8bc265) and reverted, because fresh honest answers that state the breakdown correctly lost them: 3 of 13 fresh honest breakdown answers lost points (0.7375, 0.9125, 0.9125): a free-form breakdown can put a template's figure more than 6 tokens from its name (number-first lines, an inserted parenthetical, a long clause). So they were not kept.
