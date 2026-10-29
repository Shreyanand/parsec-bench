# bench-v4-platform-041-resource-pool-unfiltered-list

Idea from bench-h4_Oct5 041 (external, 2026-10-05); re-authored; every value derived from this seed.

**Kind:** trap. `list_resource_pools` returns every pool on the cluster, and the target
is not the first row; reading the first row as the target, or reading the same-named
pool on `south`, is the targeted wrong move. Neither yields any graded number.

## What it measures

One `query_babylon_catalog` call, `action: list_resource_pools`, `cluster: east` -- the
first scenario in the suite to exercise this action. parsec lists ResourcePools from the
fixed `poolboy` namespace (`vendor/parsec/src/tools/babylon.py:53`, `_list_resource_pools`
at `:1082-1115`); no scoping parameter other than `search` (a name substring) narrows it,
and the bundle states the same: `harness-skills/parsec-platform/SKILL.md` "Store reads by
action", `list_resource_pools`: read `babylon_resource_pools`, key/filter `cluster`,
**ignore request `namespace`**, then `search`. The row shape is
`_extract_resource_pool_info` (`babylon.py:503-528`). So the agent has to pick two named
pools out of an unfiltered list and compare their sizing; an agent that passes a
`namespace` expecting a narrowed result (as it would for `list_anarchy_subjects`) gets the
full list back and must still select by name.

## Seed design

`babylon_resource_pools`, every row with `babylon_resource_pool_id` = `<cluster>-<name>`,
`cluster`, `namespace: poolboy`:

| cluster | name | min_available | max_unready | handles | role |
|---|---|---|---|---|---|
| east | acm-roadshow-pool | 4 | 2 | 9 | first row (decoy) |
| east | ansible-automation-advanced-pool | 14 | 5 | 17 | sibling |
| east | ansible-automation-bootcamp-pool | 6 | 3 | 11 | **target**, third row |
| east | devsecops-summit-pool | 13 | 7 | 15 | decoy |

Rows are listed in name order, which is the order Kubernetes and the live simulation return
them (measured 2026-10-08). The first-row decoy is named so that it sorts first.
| south | ansible-automation-bootcamp-pool | 23 | 12 | 27 | same-named twin |

Number choice is the trap's whole mechanism, so it was checked arithmetically: the graded
set is {6, 3, 11, 14, 5, 8}. No decoy row carries any graded value, and no difference a
plausible wrong pairing produces is graded either (first row vs sibling 10, south twin vs
sibling 9, twin vs devsecops 10, first row vs devsecops 9, devsecops vs sibling 1). The
pool count on east is 4 and "the two pools" says 2, both ungraded, so neither phrase can
credit a fact. Lifespans use only ungraded digits (1d/2d/4d/7d). All values satisfy the
bundle's `min_available <= resource_handle_count` and `max_unready <= resource_handle_count`.

Single digits inevitably also occur in the batch's seed; no row, name, namespace, lifespan
or combination was taken from it. `poolboy` (parsec's own constant) and the phrase
"resource handles" (the `resource_handle_count` field) are shared with the batch because
the mechanism forces them.

## Golden result

`{cluster, pools, count, truncated}` per `babylon.py:1110-1115` and the spec's
`BabylonResourcePoolListResult`; four east rows in name order, each carrying its stored
`cluster` and omitting the synthetic `babylon_resource_pool_id` (the same convention as
`bench-v4-platform-038`). **Live replay (2026-10-08):** the live call returns exactly the four east
rows, each with its `cluster`, and no south twin. **The envelope is not deterministic.** The
first replay and one raw sample were `{cluster, pools, count, truncated}`, this golden. The
re-run and a second raw sample were `{resource_pools, count, truncated}`. So the replay verdict
flips by roll (`ok` first run, `mismatch` on the re-run); the rows are identical either way. They come back **sorted by name**, not in
seed order. As first authored, the decoy was `ocp-virt-roadshow-pool`, which sorted last, so
live the first row was the sibling `ansible-automation-advanced-pool`. A first-row reader
would have reported the sibling's graded 14/5/17 instead of ungraded numbers. That was a seed
fidelity defect, because the authored first-row trap never matched the real list order. The
decoy was renamed `acm-roadshow-pool` (key `east-acm-roadshow-pool`, provider
`acm-roadshow.prod`), which sorts first, and the golden lists the rows in name order: acm,
advanced, bootcamp, devsecops. A first-row reading again yields the ungraded 4/2/9.

## Contract

- Expected call pins `action` and `cluster: east` only (both in the instruction). No
  forbidden call: querying `south` as well is not wrong, only reading its row as the answer.
- Six `answer.counts` facts, window 10, never a bare digit (hazard 5): target
  min_available 6, max_unready 3, handles 11; sibling min_available 14, max_unready 5;
  and the derived gap 8 ("by how many"). Each target fact also accepts the noun
  `bootcamp`, each sibling fact `advanced`, so a table whose header is far from its second
  row still binds the number to its pool (measured: a markdown table lost the sibling
  max_unready at window 10 before this). The handles fact also accepts `resourcehandles`,
  `resourcehandle` and `handle`, because "eleven ResourceHandles" tokenises as one word. The gap fact accepts comparison words and the
  min_available nouns, plus `14 - 6 = 8` notations via `extra_any_of`; 8 occurs nowhere in
  the seed, so a broad noun list there cannot credit a decoy.
- "Which of the two keeps the larger min_available" cannot be graded by a required name
  form: both pool names are in the instruction, so a name form would be satisfied by
  echoing it. The two min_available facts plus the gap do **not** grade the direction
  either: the gap fact's nouns accept both "more" and "fewer", so "bootcamp keeps the
  larger, by 8" satisfies it. Direction is graded only by the one forbidden fact below.
- One forbidden fact, `bootcamp-declared-larger`, `ignore_case`: eleven bare assertions
  that the bootcamp pool is the larger one ("bootcamp pool keeps the larger", "bootcamp is
  larger", "bootcamp keeps more", ...) plus 144 generated forms stating the gap in the wrong
  direction: {bootcamp, bootcamp pool, bootcamp-pool} x {keeps, has, holds, is} x {8, eight}
  x {more, higher, larger, greater, bigger, ahead}, plus 24 more (Task 8 edit pass):
  {bootcamp, bootcamp pool, bootcamp-pool} x {is higher by, leads by, is larger by, is ahead
  by} x {8, eight}. No form contains a required any_of form
  (hazard 12; the scenario has none, and `check_fact_entanglement` compares only those), and
  none is a seed literal (hazard 14). None sits inside any of the
  following negations: "the bootcamp pool is not the larger one", "Is the bootcamp pool larger? No",
  "Nor is bootcamp larger", "Advanced keeps 8 more than bootcamp", "The bootcamp pool has 8
  fewer", "Does bootcamp have 8 more? No: advanced has 8 more than bootcamp", "The bootcamp
  pool would need 8 more to match advanced" and "Is bootcamp 8 higher? No" were scored at
  1.000. The first-row and south-twin numbers are
  still not forbidden (they are seed literals and an honest answer may mention the south
  pool for contrast); those readings earn nothing and tie mute.
- Weights `0.2 / 0.8`: one call whose only discriminating argument is given by the question;
  the work is selecting and comparing rows. 0.2 is under the 0.35 cap that applies with a
  forbidden answer fact. Floors: mute 0.314, nocall 0.114, fabricate 0.200.

## Measured residuals (acceptance bar C)

Scored through this scenario's `tests/verify.py` with the golden call held correct (mute
0.314):

- The **first-row** reading (bootcamp given `acm-roadshow-pool`'s 4/2/9) typically scores
  0.543, because the same answer usually reads the sibling correctly and states its two true
  numbers. A pure first-row reading that states no true number ties mute at 0.314 (measured
  after the rename).
- A **swapped** reading (bootcamp given the advanced pool's 14/5/17 and vice versa) scores
  0.771 when it ends "Bootcamp keeps 8 more" (caught by the forbidden fact): proximity
  matching cannot bind a number to a pool name, and the swap states every true number. It
  misses the target handles (it reports 17).
- The **wrong direction** is caught for the bare assertions and the generated gap forms:
  "The bootcamp pool keeps the larger min_available, by 8", "Bootcamp keeps 8 more",
  "Bootcamp keeps eight more" and "The bootcamp pool has 8 more" each score 0.886 (they
  still state the five true numbers). "Bootcamp is higher by 8" and "Bootcamp
  leads by 8" were uncaught (1.000) until the Task 8 edit pass added the `is higher by` /
  `leads by` / `is larger by` / `is ahead by` family; they now score 0.886 like the rest.
  The only collision is a contrived verbatim negation ("It is not true that bootcamp leads by
  8"). **Uncaught:** wrong-direction phrasings outside the generated grid ("bootcamp tops
  advanced by 8", "bootcamp exceeds advanced by eight") still score 1.000.
- Reading the south twin as the target while reading the sibling correctly also scores
  0.543.
- **Pure invention can hit `sibling-max-unready` (5) by digit coincidence** ("Advanced is
  5 higher", "Difference of 5"), scoring 0.429 against mute 0.314. Structural to small
  digits near broad nouns; no zero-collision fix.
- A pure first-row, twin or "same sizing" fabrication scores 0.314 (= mute); a south-only
  call or no call scores 0.114.
