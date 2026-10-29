# bench-v5-platform-110-renamed-catalog-item

## What it measures

A chain that breaks at its second hop. The job log says the catalog item
`appdev_bu/devsecops-pipeline-lab` could not be loaded. `lookup_catalog_item` returns
`found: false`, with one near match, `devsecops-pipeline-lab-partner`: a different
partner item that an agent might substitute to "complete" the chain. Recovery needs a
pull-request search *that is not restricted to open PRs*:

- the default `state` (`open`) returns nothing;
- `state: all` (or `closed`) returns the closed PR #6123, "Rename devsecops-pipeline-lab
  to secure-supply-chain-lab".

The job template still launches the old name.

## Grounding

- `query_aap2 get_job_log` (`east`, `726350`): composite `jobs` read.
- `lookup_catalog_item` (`search` unpinned; the golden path uses `devsecops-pipeline-lab`).
  The stored `catalog_items` row for that directory has `found: false` and a message. The
  near matches are the stored `similar_items` rows whose normalised name contains the
  normalised search, which leaves only the partner decoy; `secure-supply-chain-lab` does
  not contain the old name. `gen_110.py` asserts this.
- `search_agnosticv_prs`: the keyword is a substring of #6123's title, so all its files
  are returned (github SKILL.md matching rule). With `state` omitted, the effective state
  is `open`. #6123 is `closed` and #6158 (open) matches neither its title nor its files,
  so the result is `count: 0`. With `state: all`, #6123 is returned. `gen_110.py`
  asserts both. The golden path makes both calls. The expected spec leaves `state`
  unpinned, so either `all` or `closed` satisfies it, and the PR number is what grades
  the recovery.
- **Forbidden call:** `search_agnosticv_prs` with `state: merged`. "merged" is GitHub
  vocabulary, but not one of `open`/`closed`/`all`, so it is the documented in-band error.
  The instruction's "whatever its state" invites it.
- **validate.py WARN, justified:** `repos_searched` values (`rhpds/partner-agnosticv`
  etc.) are "not in seeds". They are the documented constant array (SKILL.md Derivation
  Rules), not seed data.

## Contract

- Expected calls: ordered-subsequence, log, then lookup, then PR search. Weights 0.25/0.75 (0.3/0.7 at import; reweighted 2026-10-13, see Changes after import).
- Required:
  - `not-found`: the break, reported.
  - `pr-number` (6123): needs a non-default state.
  - `new-name`: only in the PR.
  - `stale-template`: derived.
- Forbidden facts: `decoy-substituted` (assertions that the partner item is the lab) and
  `pending-pr` ("PR is still open", "waiting to be merged" and similar). Neither has
  `attributed_to`.

## The wrong answer

> not found ... renamed to devsecops-pipeline-lab-partner; use devsecops-pipeline-lab-partner
> instead. I found no pull request touching it, so the PR is still open somewhere,
> waiting to be merged.

With the golden calls: **0.4167** (answer 0.167). With the wrong transcript (the PR
search with `state: merged`): **0.1167**.

## Invented

Every literal is invented for bench-v5: job 726350, GUID `b2rwn`, account `appdev_bu`,
the item names, the partner account, PRs #6123 and #6158, their authors, branches and
timestamps, and the git revision.
