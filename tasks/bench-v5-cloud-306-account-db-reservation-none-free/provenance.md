# bench-v5-cloud-306-account-db-reservation-none-free

**Kind:** negative. **Calls:** 1. **Weights:** 0.2 / 0.8.

## What it measures

A non-finding read from the sandbox account DB's scan path. The user needs 4 free
accounts from the `gpu-ee` reservation. All three `gpu-ee` accounts are `available: false`,
so the honest answer is zero free, plus who holds them (the user asks for that).

`reservation` is a case-insensitive substring filter, so `reservation: "gpu-ee"` also
returns the two free accounts of `gpu-ee-dryrun`. The same happens with
`available: true`, where those two are the only rows returned. An agent that trusts the
filter reports "2 free" and is two short rather than four short.

## Grounding

- cloud SKILL.md `/query_aws_account_db POST`:
  - Without `name`, it scans `sandbox_accounts`. `account_id`/`available` are exact
    filters, and `owner`/`zone`/`envtype`/`reservation` are "case-insensitive substring"
    filters.
  - `max_results` defaults to 100.
  - Rows are returned as stored minus `sandbox_account_id`, with envelope
    `{accounts, count, truncated}`.
- Golden call `{reservation: "gpu-ee"}` returns 5 rows in seed order (3 gpu-ee, 2
  gpu-ee-dryrun). No argument is pinned, since an agent may pass `available` or scan
  everything.
- Seed: 7 rows. Besides the five above, one free general-pool account and one assigned
  `summit-labs` account. Free rows carry `""` for owner/email/envtype/guid, with no nulls.

## Contract

- Required:
  - `holder-jhalvorsen`, `holder-emugisha`, `holder-mlindqvist`: who holds the gpu-ee
    accounts (asked).
  - `dryrun-is-different` (derived): names `gpu-ee-dryrun`, which is how an answer
    separates the decoy rows from gpu-ee.
- Count `gpu-ee-free` = 0 (nouns free/available accounts). `extra_any_of` takes
  numeral-free forms ("none are free", "all three are assigned", ...).
- Forbidden `dryrun-counted-free`: asserting 2/two accounts are free or available, or
  that sandbox9420/9421 are free in gpu-ee. `attributed_to` is limited to the decoy's own
  name (`gpu-ee-dryrun`, `dryrun`, `dry-run`, `dry run`). A sentence that names the other
  reservation is attributing the rows correctly. Probe `.scratch/wrong/p306.md`
  ("Although the filter was fuzzy, 2 accounts are free in gpu-ee.") is hit.
- Floors: mute 0.17, echo 0.17.

## The wrong answer

`.scratch/wrong/w306.md`: "2 accounts are free: sandbox9420 and sandbox9421 ... 2 short".
With golden calls: reward **0.60**. It misses dryrun-is-different and the zero count, and
hits the forbidden fact.

## Invented

Every literal is invented: sandbox names, account ids, holders, emails, zones, GUIDs and
reservations. Nothing comes from bench-v4 or from production data.
