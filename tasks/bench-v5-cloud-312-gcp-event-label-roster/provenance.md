# bench-v5-cloud-312-gcp-event-label-roster

**Kind:** happy. **Calls:** 1. **Weights:** 0.2 / 0.8.

## What it measures

Selecting rows by a label value that the tool cannot filter on. `query_gcp_projects`
`list_projects` filters only by `state_filter`, so a roster for one event has to be
picked out of the folder listing by each project's `labels.event`. The folder holds 9
projects: 4 labelled `event: fjord-devdays-2610` (3 ACTIVE, 1 DELETE_REQUESTED), 3
labelled `atlas-bootcamp-2610`, and 2 with no event label. The answer names the four
event projects, gives their states (one is DELETE_REQUESTED), and counts 3 still ACTIVE,
against the listing's folder-wide `active: 7`. A happy path: the label is given in the
instruction, and the work is client-side selection plus per-row reading.

## Grounding

- cloud SKILL.md `/query_gcp_projects POST`:
  - `list_projects` reads `gcp_projects` as the complete dataset and filters only by
    `state_filter` (case-insensitive on `state`) when given. It projects each row to
    `project_id, name, state, create_time, labels`.
  - Derived fields: `count` is `len(projects)`, `active` the ACTIVE rows, and
    `delete_requested` is `count - active`. `folder_id` is the configured folder id, or a
    hard-coded default.
- Seed: 9 `gcp_projects` rows, all with `parent: folders/739201846553`. The golden
  `folder_id` uses that id, as bench-v5-cloud-301 does for its folder.
- Golden result: all 9 rows in seed order; `count 9, active 7, delete_requested 2,
  truncated false`. 9, 7 and 2 are documented derived aggregates.
- The expected call pins only `action: list_projects`. An agent that adds
  `state_filter: ACTIVE` would never see `rhdp-ws-w5kcz` and so could not report its
  state; the contract catches that in the answer, not by pinning the absence of a filter.

## Contract

- `proj-q2nvx`, `proj-j7tfa`, `proj-w5kcz`, `proj-b9hmu` (required): the four project ids
  with the label ("Which projects have that label"). Only the listing names them.
- `w5kcz-delete-requested` (required): the DELETE_REQUESTED state, with plain-English
  equivalents ("what state is each one in"). It is the one non-ACTIVE state among the
  four, so it is what separates a full per-row read from an ACTIVE-only one.
- `event-active-count` (count 3; nouns ACTIVE / active / still active / still running /
  running; window 6; extra_any_of "3 of the 4" and kin): "how many of them are still ACTIVE". The neighbouring figures are
  7 (folder-wide `active`) and 4 (the event's projects).
- No forbidden fact: a happy path, and the over-inclusive error (an atlas project named
  as an event project) would name a seed literal (hazard 14). The count carries it.
- `fold_markup` is on, so backticked ids match.
- Weights 0.2 / 0.8.

## The wrong answer

`/tmp/ext/scratch/cloud-312/wrong.md`: the agent filters on `state_filter: ACTIVE`, picks
the three labelled rows and reports "the event has 3 projects, all ACTIVE", omitting
`rhdp-ws-w5kcz`. It misses `proj-w5kcz` and `w5kcz-delete-requested`. A second wrong
answer, `/tmp/ext/scratch/cloud-312/wrong2.md`, quotes the folder-wide "7 active" as the
event's figure. Measured with `score_answer.py` and the golden calls: wrong.md reward
**0.733** (answer 0.667), wrong2.md reward **0.867** (misses only the count). Two fresh
honest answers (terse prose; a table with `Key: value` count that rejects the folder-wide 7)
score 1.000. Floors (validate.py): golden 1.000, mute 0.200, nocall 0.000, fabricate n/a.

## Invented

Every literal is invented: the folder id, project ids, GUIDs, event labels, owners and
timestamps. `ACTIVE` and `DELETE_REQUESTED` are real GCP Resource Manager states.
Nothing comes from bench-v4 or from production data.
