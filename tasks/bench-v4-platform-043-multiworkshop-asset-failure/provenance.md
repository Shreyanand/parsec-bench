# bench-v4-platform-043-multiworkshop-asset-failure

Idea from bench-h4_Oct5 043 (external, 2026-10-05); re-authored; every value derived from this seed.

**Kind:** trap. The namespace holds two MultiWorkshop events of the same
academy, Wave 6 and Wave 7, each with exactly one child workshop that failed
to provision. The instruction names neither resource. An agent that takes the
wrong parent (or reads the wrong children) reports `aa6-network`, job `70222`
and a count of 3, and earns nothing; an agent that stops at the listing sees
`asset_count` but no provisioning state at all.

## What it measures

A two-hop chain, the suite's first expected use of `list_multiworkshops` and
`get_multiworkshop`:

1. `query_babylon_catalog` `list_multiworkshops` `{cluster: nordic,
   namespace: user-hlindqvist-redhat-com}` -- both values are in the
   instruction. `search` is not pinned (hazard 19): an agent that searches
   "wave 7" or "academy" or lists unfiltered has done the same work.
2. `query_babylon_catalog` `get_multiworkshop` `{cluster: nordic, namespace:
   user-hlindqvist-redhat-com, name: automation-academy-w7}`. The `name`
   appears only in call 1's result (`check_expected_calls_derivable`), picked
   out of two rows by its display name "Automation Academy - Wave 7".

Mechanism, from parsec:

- `vendor/parsec/src/tools/babylon.py:1372-1420` (`_list_multiworkshops`):
  `namespace` is required (`:1379-1383`); each row is
  `_extract_multi_workshop_info` (`:596-626`) -- name, display_name,
  number_seats, dates, purpose, `assets` and `asset_count = len(assets)`.
  Nothing in the listing says whether a workshop provisioned.
- `babylon.py:1423-1545` (`_get_multiworkshop`): fetches the MultiWorkshop,
  lists child Workshops by label selector
  `babylon.gpte.redhat.com/multiworkshop=<name>` in the event's namespace
  (`:1493-1501`), and for each child returns name, display_name,
  catalog_item, workshop_id, `provision_count` (`_extract_provision_count`,
  `:531-541`) and `resource_claims` traversed by `_fetch_resource_claims`
  (`:1164-1195`) to `resources[].tower_jobs.provision.{controller, job_id,
  status, completed}` (`_extract_anarchy_state`, `:388-415`). It closes with
  `summary {total_workshops, active, failed}` (`:1538-1542`).
- `harness-skills/parsec-platform/SKILL.md`, `/query_babylon_catalog`, "Store
  reads by action": `list_multiworkshops` reads `babylon_multiworkshops`
  filtered by `cluster`, then `namespace`; `get_multiworkshop` reads the
  parent from `babylon_multiworkshops` and its children from
  `babylon_workshops` "where `cluster` = parent `cluster` and `namespace` =
  parent `namespace` and `multiworkshop` = parent `name`". The Derivation
  Rules repeat it and say the child count equals the number of such rows.
  There is no separate claim collection: as in `bench-v4-platform-040`, the
  traversed claims are the stored child row's `resource_claims` field, so the
  failed claim and its integer AAP2 job id are seeded inline there.

## Seed design

`seeds/platform.json` carries the full platform collection set; only
`babylon_multiworkshops` and `babylon_workshops` are non-empty, and
`workshops` is `[]`. Everything is on cluster `nordic`, namespace
`user-hlindqvist-redhat-com`.

| parent | children (`multiworkshop` = parent) | failed child | its provision job |
|---|---|---|---|
| `automation-academy-w6` (decoy, Wave 6, 36 seats) | aa6-linux-core, aa6-network, aa6-cloud | aa6-network | 70222 |
| `automation-academy-w7` (target, Wave 7, 60 seats) | aa7-linux-core, aa7-network, aa7-windows, aa7-eda, aa7-security | aa7-windows (claim aa-windows-prod-x2k7r, provision-error) | 73419 |

Each child has one claim; healthy claims carry successful provision jobs
73406/73411/73423/73430 (Wave 7) and 70215/70230 (Wave 6). Each parent's
`assets` list mirrors its children (`workshop_id` ties asset to workshop),
so `asset_count` is 3 and 5. The decoy is stored first. No Windows workshop
exists in Wave 6, so the failed-workshop forms cannot be met by a decoy
reading.

Golden results: call 1 returns both rows as parsec projects them plus the
stored `cluster` (synthetic `babylon_multiworkshop_id` omitted). Call 2 is
parsec's `_get_multiworkshop` shape: the eight parent fields with
`number_seats` renamed `seats`, five children, and `summary {5, 4, 1}`.
**Live replay (2026-10-08): the response shape is not deterministic.** Two raw samples of the
same seed disagreed. One was exactly this golden: parsec's projection, plus `requester: ""`,
which the replay ignores. The other returned the stored rows unprojected:
`list_multiworkshops` without top-level `cluster`/`namespace`, and `get_multiworkshop` with
`number_seats`/`asset_count`/`assets`/`workshops_count`, no `seats` and **no `summary`**, and
full stored child rows. The replay's first run matched neither shape on both attempts (`$.cluster`
and `$.namespace` missing on call 1, `$.seats` and `$.summary` missing on call 2). Both shapes
carry the same content: exactly the five w7 children, no w6 leak, `resource_claims` exactly as
stored. The golden keeps parsec's shape, which is ground truth and one of the live shapes, so
this scenario's replay verdict flips between `ok` and `mismatch` by roll. On the
unprojected roll, the agent has no `summary.failed` and has to find the failed child in its
claims (`provision-error`, job 73419 `failed`). The graded facts already require that.
`requester` is omitted: `BabylonMultiworkshop` has no such stored field and
the replay tolerates extra keys, so the golden result does not guess it.

## Contract

Weights `0.3 / 0.7`: call 1's arguments are handed over by the instruction,
call 2's `name` must be picked out of call 1; the difficulty sits in reading
the right parent's children. No forbidden call, no forbidden fact (a
decoy reading earns nothing on its own, so a forbidden list would add only
free mute credit).

- `failed-workshop` (required): `aa7-windows` / `aa7 windows` /
  `aa7_windows` / `windows automation`, ignore case.
- `child-count` (counts): value 5, nouns workshops, children, child, assets,
  labs, total_workshops, sub-workshops, subworkshops, members; window 10.
- `failed-job-id` (counts): value 73419, the job nouns used across the
  suite; window 10.

S7: no required form occurs in `instruction.md`. Batch overlap: `windows`
occurs only in the batch's unrelated `seeds/cost.json`; "child workshops" is
the mechanism's own term, occurring in the batch's provenance prose. No seed
value, id, name or number is shared with the batch or with 037/038/040-042/044.

## Gate and probes

Gate: golden 1.000, mute 0.300, nocall 0.000, fabricate n/a.

Twelve honest paraphrases (digits and words, tables, key-value, markdown,
"four of the five", "1 of 5", "apart from", snake_case name, no-terminator
endings) score 1.000. Fabricators and decoy readings (Wave 6 values, wrong
child, "none failed", "several workshops") score 0.300 or 0.150.

**Measured residuals (bar C, true literal stated):**
- An agent that stops after `list_multiworkshops` can quote `asset_count 5`
  and earns the count fact: 0.383 (one call) against mute 0.300. The count is
  graded because the instruction asks for it; it is true in both calls.
- A correct count paired with the decoy's failure (`aa6-network`, 70222)
  scores 0.533.
- An answer listing every child's provision job id earns the job fact as
  long as 73419 is among them, as in 040.
- **A full child dump scores 1.000 without naming the failure** (measured
  2026-10-08): "automation-academy-w7 children: aa7-linux-core (job 73406),
  aa7-network (job 73411), aa7-windows (job 73419), aa7-eda (job 73423),
  aa7-security (job 73430). 5 workshops." earns all three facts, because each
  is a literal that occurs in the dump; nothing grades the claim *that*
  aa7-windows is the one that failed. Forbidding it would need a form
  containing a required literal (hazard 12).
- An answer that gives the right count and says every workshop provisioned
  ("automation-academy-w7 has 5 child workshops, and all of them provisioned
  successfully") scores 0.533 against mute 0.300: it states the true count.
