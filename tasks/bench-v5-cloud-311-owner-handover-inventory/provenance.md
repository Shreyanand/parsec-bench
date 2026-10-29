# bench-v5-cloud-311-owner-handover-inventory

**Kind:** happy. **Calls:** 1. **Weights:** 0.2 / 0.8.

## What it measures

A person-scoped inventory read from the sandbox account DB. A manager handing over a
departing engineer's work asks for every AWS sandbox account recorded under her
username, with each one's AWS account id and env type, and the total. The natural route
is `query_aws_account_db` with the `owner` filter, a case-insensitive substring match on
`owner` (falling back to `owner_email` when `owner` is empty). It returns the four rows
owned by ovelasquez out of eight in the store. The discrimination is completeness and
per-row reading: four distinct account ids, four distinct env types, and the count.
No existing task selects sandbox accounts by owner.

## Grounding

- cloud SKILL.md `/query_aws_account_db POST`:
  - Inputs: `owner` "When `name` is not provided, apply as a case-insensitive substring
    filter. Match against `owner`; when a row's `owner` is empty, fall back to
    `owner_email`."
  - Store access: "Read `sandbox_accounts` as a collection scan", then the substring
    filters, then the `max_results` cap (default 100).
  - Projection: "Return each matched stored row ... exactly as stored, **except** omit
    `sandbox_account_id`." `count` is `len(accounts)`.
- Seed: 8 `sandbox_accounts` rows. Four have `owner: ovelasquez` (sandbox8061, 8064,
  8067, 8070). The others are owned by akimura, bcho and lpetrov, and one free row
  (sandbox8063) has blank `owner` and `owner_email`, so the fallback matches nothing.
- Golden call `{owner: "ovelasquez"}`. Its result is the four rows, in seed order, minus
  `sandbox_account_id`; `count 4, truncated false`.
- The expected call pins no argument. An agent that scans the whole collection (no
  filter, 8 rows) and selects the rows itself is equally right; pinning `owner` would
  mark that correct route wrong.

## Contract

- `acct-8061`, `acct-8064`, `acct-8067`, `acct-8070` (required): the four AWS account ids
  ("giving the AWS account id"). Only the tool result holds them.
- `envtype-8061` ... `envtype-8070` (required): `ocp4-hcp-workshop`, `rhel10-beta-lab`,
  `ansible-lightspeed-demo`, `ocp4-acm-gitops` ("the env type each one runs"). They are
  distinct, so each has to be read from its own row. akimura's sandbox8062 also runs
  `ocp4-hcp-workshop`, which does not matter: naming it is correct for sandbox8061.
- `owned-count` (count 4; nouns accounts / sandbox accounts / sandboxes / sandbox / aws
  accounts / in total / total; window 4): "tell me how many there are in total". The
  store holds 8 rows, so the plausible miscounts are 3 (a dropped row) and 8 (no
  selection).
- No forbidden fact: a happy path, and every wrong literal (another owner's account) is
  in the seed (hazard 14). The count carries the over-inclusion error.
- `fold_markup` is on, so backticked ids match.
- Weights 0.2 / 0.8: one call, and the answer carries the content.
- Floors (validate.py): golden 1.000, mute 0.200, nocall 0.000, fabricate n/a.

## The wrong answer

`/tmp/ext/scratch/cloud-311/wrong.md`: an answer that lists three of the four accounts
(drops sandbox8070) and says "3 sandbox accounts". It misses `acct-8070`,
`envtype-8070` and `owned-count`. Measured with `score_answer.py` and the golden calls:
answer 0.667, reward **0.733**. Two fresh honest answers (terse prose; a markdown table
that also rules out akimura's sandbox8062) score 1.000.

## Invented

Every literal is invented: the person, usernames, sandbox names, AWS account ids, env
types, GUIDs, zones, comments and the date. Nothing comes from bench-v4 or from
production data.
