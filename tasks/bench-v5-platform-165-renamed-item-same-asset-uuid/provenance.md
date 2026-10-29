## What it measures

Joining a deployment to the catalog by `asset_uuid`, the identity that survives a rename. Two
sibling calls on `petrel`:

1. `list_deployments {cluster: petrel, namespace: user-hvasquez-redhat-com}` returns the user's
   claim `edgefleet-ota-lab-q7rbn`: `catalog_item: edgefleet.ota-lab.prod`, `asset_uuid:
   5e1c9a47-3b02-4d8e-a6f1-0c7d92b4e813`.
2. `search_catalog {cluster: petrel}` returns three items. None is named `edgefleet.ota-lab`:
   - `edgefleet.ota-updates`, "Edgefleet Over-the-Air Updates", carries the **same** asset UUID.
     This is the renamed item.
   - `edgefleet.ota-lab-emea` keeps the **old title**, "Edgefleet OTA Lab", but its asset UUID is
     `d2b8e05c-...`. It is a different item, and it is the lure: the user's own words ("the
     Edgefleet OTA lab") match its title and its name is a prefix extension of the old one.

The old name is still published on another cluster, `tern`. Cluster filtering keeps it out.

Answer: ordered from `edgefleet.ota-lab.prod`; it now lives on as `edgefleet.ota-updates`
("Edgefleet Over-the-Air Updates"); the shared asset UUID proves it.

Behaviour: **a renamed catalog item is found by the deployment's `asset_uuid`, not by its name
or title; the old title now belongs to a different item.** No count.

## Grounding

- platform SKILL.md `/query_babylon_catalog`: `list_deployments` reads `babylon_deployments`,
  filtered by `cluster` and then `namespace`. Response keys `{cluster, namespace, deployments, count,
  truncated}`; no element carries `cluster` or the `_id` key.
- `search_catalog` reads `babylon_catalog_items` filtered by `cluster`, projected to exactly
  `ci_name`, `display_name`, `namespace`, `stage`, `multiuser`, `asset_uuid` and `keywords`, with
  envelope `{cluster, items, count, total_scanned, truncated}`. `total_scanned` is 3: the `tern` row
  is filtered out before scanning.
- parsec: `_extract_deployment_info` takes `asset_uuid` from the claim's `gpte.redhat.com/asset-uuid`
  label, and `_parse_catalog_item` takes it from the CatalogItem's (`vendor/parsec/src/tools/
  babylon.py:121-145`, `:347-363`), so the two are the same label on both resources.
- List order is by name in the golden results.

## Contract

- Calls, `unordered-subset` (independent siblings): `list_deployments` pins `cluster` and
  `namespace`; `search_catalog` pins `cluster`. All values are in the instruction. `search` is not
  pinned.
- Forbidden call: `get_catalog_item`. It is not an action in the api.json enum, and the in-band
  result is `Unknown action`.
- Required: the ordering item `edgefleet.ota-lab.prod` (only in the deployment), the current name
  `edgefleet.ota-updates`, its title "Over-the-Air Updates", and the asset UUID (full or its first
  group). `fold_markup` is on, because agents wrap names in backticks.
- Forbidden (`wrong-successor-or-pulled`): asserting the emea fork is the successor ("renamed to /
  now called / order edgefleet.ota-lab-emea") or that the item was pulled. Every form is an
  assertion; honest denials ("not pulled", "is not the successor") are excused by polarity.
- Weights 0.3/0.7. Gate: golden 1.000, mute 0.440, nocall 0.140, fabricate 0.300.

## The wrong answer

"Your lab came from `edgefleet.ota-lab.prod`. On petrel that item was renamed to
`edgefleet.ota-lab-emea`; it still carries the same title, so that's the entry your colleague
should order." Scores **0.440** with the golden calls (one required fact, forbidden hit). An answer
saying the item was pulled with no replacement also scores 0.440. Two fresh honest answers, terse
prose and a table that denies the emea fork, both score 1.000.

## Invented

The cluster names `petrel` and `tern`, the namespace, GUIDs, claim and item names, titles, asset
UUIDs and timestamps are all invented. Nothing comes from bench-v4 or production data.
