# bench-v4-platform-044-search-catalog-env-type

Idea from bench-h4_Oct5 044 (external, 2026-10-05); re-authored; every value derived from this seed.

**Kind:** trap. The AWS and GCP editions of one lab share a base name in the
catalog. An agent that searches by the lab's name without the `env_type` filter
gets both, and handing back the GCP edition as the AWS one is penalised.

## What it measures

One call, and the suite's first expected use of `search_catalog`:
`query_babylon_catalog` with `action: search_catalog`, `cluster: east`,
`env_type: aws`.

- `vendor/parsec/src/tools/babylon.py:782-825` (`_search_catalog`) lists
  CatalogItems from all three `CATALOG_NAMESPACES` (`babylon.py:31`), parses
  each with `_parse_catalog_item` (`babylon.py:121-145`), then applies two
  independent client-side filters. `search` is a case-insensitive substring
  over `ci_name`, `display_name` and `keywords` (`:809-812`). **`env_type` is a
  case-insensitive substring over `ci_name` only** (`:813-814`). There is no
  `env_type` field on a catalog item. The result is
  `{cluster, items, count, total_scanned, truncated}` (`:819-825`).
- `harness-skills/parsec-platform/SKILL.md`, `/query_babylon_catalog`, "Store
  reads by action": `search_catalog` reads `babylon_catalog_items`, filters by
  `cluster` first, then `search` over `ci_name`/`display_name`/`keywords` and
  `env_type` as a substring over `ci_name`. `namespace` is not a filter for
  this action.

**Does `env_type: aws` return the GCP twin?** No. Its `ci_name`
(`summit-labs.edge-observability-gcp`) does not contain `aws`, so per
`babylon.py:813` and SKILL.md the filter drops it. The golden result therefore
holds the three east rows whose `ci_name` contains `aws`: the target and two
different AWS labs. The GCP twin reaches only an agent that searches without
`env_type` (for example `search: edge observability`, which returns both
editions). For that agent the trap is which row it picks. For an agent that
follows the instruction, the task is picking the right one of three AWS rows,
since `search` is left unpinned and the instruction names the lab by display
name only.

`env_type` and `cluster` are pinned. Both are in the instruction, so
`check_expected_calls_derivable` passes. The instruction asks for the
`env_type` filter outright. The id names that filter as the scenario's subject,
and an agent that skipped it while answering correctly would otherwise lose the
tool component for an honest answer (probe H8 measures exactly that case at
0.700). `search` is never pinned (hazard 19).

## Seed design

`seeds/platform.json` declares every collection in the platform `schema.json`.
All are empty except `babylon_catalog_items`, and each row carries
`babylon_catalog_item_id` and `cluster`:

| id | cluster | ci_name | namespace / stage | asset_uuid |
|---|---|---|---|---|
| east-edge-observability-aws | east | `summit-labs.edge-observability-aws` | babylon-catalog-event / event | `3f696994-…1c00` (**target**) |
| east-edge-observability-gcp | east | `summit-labs.edge-observability-gcp` | babylon-catalog-prod / prod | `2a6fc78f-…3bfc` (GCP twin) |
| east-edge-manager-aws | east | `summit-labs.edge-manager-aws` | babylon-catalog-prod / prod | `b6cb7e9c-…` (other AWS lab, similar prefix) |
| east-satellite-patching-aws | east | `sandboxes-gpte.satellite-patching-aws` | babylon-catalog-dev / dev | `123be796-…` (other AWS lab) |
| east-satellite-patching-azure | east | `sandboxes-gpte.satellite-patching-azure` | babylon-catalog-prod / prod | `79193a2b-…` (excluded by env_type) |
| west-edge-observability-aws | west | `summit-labs.edge-observability-aws` | babylon-catalog-prod / prod | `3f696994-…1c00` (scope decoy) |

- The target is the only `env_type=aws` match on east in
  `babylon-catalog-event`. The GCP twin, the west copy and both other AWS labs
  are elsewhere, so the namespace fact separates every wrong reading.
- The west copy shares the target's `ci_name` and asset UUID, which is realistic:
  the asset UUID labels the catalog item, not the cluster. Only its namespace
  differs. It is there for the live replay (Review Focus 3). A simulation that
  leaked it into an east search would return four items against the golden
  three, and the length-exact list comparison would flag it.
- `total_scanned` in the golden result is 5, the east rows before filtering,
  which is parsec's `len(all_items)` for this cluster. **Live replay (2026-10-08): the
  envelope is not deterministic.** One raw sample was exactly this golden (`{cluster, items,
  count, total_scanned, truncated}`). Another returned `{catalog_items, count, truncated}`: no
  `cluster`, `items` renamed and no `total_scanned`. Both replays mismatched on the envelope
  only. Every sample returned exactly the three east AWS rows, each with `cluster`, and no west
  leak. The golden keeps parsec's shape, so the replay verdict flips by roll; nothing graded
  depends on the envelope. Golden items omit the
  synthetic `babylon_catalog_item_id`, as 041's golden does with
  `babylon_resource_pool_id`. Replay allows extra live keys.
- `summit-labs` is an invented agnosticv account, chosen over parsec's real
  `zt-rhelbu`. parsec's `shared_context.md:33` teaches that `*-zt-*` sandboxes
  are OpenShift CNV, and that would muddy an AWS/GCP question.
  `sandboxes-gpte` is parsec's own account name (`docs/ARCHITECTURE.md:194`).
  It also appears in the batch's default github seed, but it was taken from
  parsec, not from the batch.
- The three namespace names are parsec's `CATALOG_NAMESPACES` (`babylon.py:31`).
  `babylon-catalog-event` also appears in the batch's provenance, which is
  forced by the mechanism. `east`/`west` are the suite's standing Babylon
  cluster names. "env_type" and "asset UUID" in the instruction are the
  argument name and the field (`asset_uuid`). Every other literal (lab names,
  display names, UUIDs, keywords) is new, and S7 found none of them in the
  batch's directory.

## Contract

Weights `0.3 / 0.7`. One forbidden fact means the tool weight must stay ≤ 0.35.
The call is half the challenge (the right filter on the right cluster) and
the selection is the other half. Floors: mute 0.475, nocall 0.175,
fabricate 0.300.

Required (all `ignore_case`; none occurs in `instruction.md`):

- `aws-ci-name`: `edge-observability-aws`. This is a substring of the full
  ci_name, so the bare and account-qualified forms both count.
- `aws-asset-uuid`: `3f696994-5b7b-4e6f-8056-435d13ca1c00`.
- `aws-namespace`: `babylon-catalog-event`.

An agent that picks the GCP twin earns none of these, and neither does one that
picks either other AWS lab. The required facts can't be earned for free, so a
fabrication the forbidden list misses ties mute rather than beating it.

Forbidden `gcp-twin-named-as-aws`: ten forms that bind the GCP twin's full
ci_name to the AWS edition: `aws {edition|build|item|version|catalog item|variant}
is summit-labs.edge-observability-gcp`, plus backticked and bold variants of
`aws edition is`, and `aws edition of the edge observability lab is …` with and
without a backtick. The bare twin ci_name is a seed literal, so it cannot be
forbidden (hazard 14). The forms contain no required form, and none occurs in
the seed. They are deliberately few and high-precision: a natural fabricator
written as a bullet list (`- ci_name: summit-labs.edge-observability-gcp`)
is **not** caught, because an honest answer listing what it excluded can use
the same notation. That fabricator states no true graded literal, so it ties
the mute floor (F2/F8 below score 0.175 because they also skipped `env_type`).

## S9b probes (scored through `tests/verify.py`)

Calls: GOLD = `{search_catalog, east, env_type: aws}`. GOLDS = GOLD plus
`search: edge observability`. NOENV = `{search_catalog, east, search:
edge-observability}`. Mute floor 0.475.

| probe | calls | answer (abridged) | reward |
|---|---|---|---|
| H1 | GOLD | "The AWS edition is <aws ci_name>. Asset UUID <uuid>, published in babylon-catalog-event." | 1.000 |
| H2 | GOLDS | markdown table, backticked values, UUID upper-cased | 1.000 |
| H3 | GOLD | bold key-value bullets + "Not the GCP twin <gcp ci_name> (asset <gcp uuid>), which lives in babylon-catalog-prod and is excluded" | 1.000 |
| H4 | GOLD | "apart from <aws>, the other two (edge-manager-aws, satellite-patching-aws) are different labs. So: …" | 1.000 |
| H5 | GOLD | "The AWS edition is not <gcp> -- that is the GCP edition. The AWS edition is <aws> …" | 1.000 |
| H6 | GOLD | `ci_name = … / asset_uuid = … / namespace = …` | 1.000 |
| H7 | GOLD | bare `edge-observability-aws`, "asset-uuid label", "Babylon-Catalog-Event" | 1.000 |
| H8 | NOENV | correct answer after an unfiltered search, "The GCP variant is excluded" | 0.700 (tool 0: skipped the instructed filter) |
| H9 | GOLD | backticked; "The GCP edition <gcp> is not the AWS edition and was not returned" | 1.000 |
| H10 | GOLD | slash-separated triple + "the AWS edition is <aws>, not <gcp>" | 1.000 |
| H11 | GOLD | "AWS edition's ci_name is …; … (west has a copy in babylon-catalog-prod)" | 1.000 |
| H12 | GOLD | "The AWS edition of the Edge Observability lab is <aws>, not the GCP twin <gcp>." | 1.000 |
| F1 | NOENV | "The AWS edition is <gcp>. Asset UUID <gcp uuid>, published in babylon-catalog-prod." | 0.000 |
| F2 | NOENV | bullet list of the GCP twin's three values | 0.175 |
| F3 | GOLD | "The AWS edition of the Edge Observability lab is `<gcp>` …" | 0.300 |
| F4 | GOLD | the edge-manager-aws row's values (wrong AWS lab) | 0.475 |
| F5 | GOLD | invented ci_name, invented UUID, prod | 0.475 |
| F6 | GOLD | content-free "I found it and reported …" | 0.475 |
| F7 | GOLD | "No AWS edition exists on east; only a GCP build is published." | 0.475 |
| F8 | NOENV | "<gcp> is the one you want: …" | 0.175 |
| F9 | GOLD | "The AWS build is <gcp> (UUID …), namespace babylon-catalog-prod." | 0.300 |
| F10 | none | correct values with no call at all | 0.700 |
| W1 | GOLD | the west copy's values (shared ci_name and UUID, namespace prod) | 0.825 |

Measured residuals (acceptance bar C): W1 states two true graded literals,
because the west copy really shares the target's ci_name and asset UUID, and it
misses only the namespace. A real west-reading agent would also have called
`cluster: west` and lost the tool component, which measured 0.525 (still above mute; no zero-collision form closes it, because honest answers name the excluded rows' `babylon-catalog-prod` in the same notations). F10 is an answer with no
call that is right by luck, and it cannot happen without seeing the seed. F4
and F7 tie mute (bar B).
