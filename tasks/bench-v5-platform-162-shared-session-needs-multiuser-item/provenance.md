## What it measures

Picking a catalog item by its `multiuser` flag rather than by its name. One call:
`query_babylon_catalog {action: search_catalog, cluster: avocet}`.

The user wants **one** environment that all 25 attendees share. avocet has two OpenShift AI items,
both `stage: prod`:

- `rhoai.datasci-workshop`, "Red Hat OpenShift AI Workshop": the name invites the pick, but it has
  `multiuser: false`, so each attendee gets their own environment;
- `rhoai.model-serving-lab`, "OpenShift AI Serving Lab": `multiuser: true`, asset UUID
  `8c41f2d7-e05b-4a9c-9f63-2b7d18e4c5a0`.

On another cluster, `curlew`, the same-named "Workshop" item *is* `multiuser: true`. Cluster
filtering keeps that row out of the avocet result.

Behaviour, for the authors of 165-169: **`search_catalog`'s `multiuser` field decides the item;
the title "Workshop" is the lure.** No count.

## Grounding

- platform SKILL.md `/query_babylon_catalog`: `search_catalog` reads `babylon_catalog_items` filtered
  by `cluster`. Rows are projected to exactly `ci_name, display_name, namespace, stage, multiuser,
  asset_uuid, keywords`. The response is `{cluster, items, count, total_scanned, truncated}`, and
  `total_scanned` counts the rows after cluster scoping and before the filters, as parsec does
  (`vendor/parsec/src/tools/babylon.py:823`).
- `schema.json`: `multiuser` is "Whether the item supports multiuser workshop provisioning". parsec
  reads `spec.multiuser` (`babylon.py:142`). A multiuser item is one shared environment for many
  users, which is exactly what the instruction asks for in plain words, without naming the field.
- The golden call is unfiltered, so it returns all four avocet rows in name order. `search` is not
  pinned (hazard 19): searching "openshift ai" returns the same two candidates.

## Contract

- One expected call, `search_catalog {cluster: avocet}`.
- Required:
  - the item, `rhoai.model-serving-lab` or its display name;
  - its asset UUID;
  - the reason, "multiuser" / "multi-user". The instruction asks "what in the catalog record makes
    it the right one" and never says the word.
- No forbidden facts: the decoy's name is a seed literal (hazard 14), and the required facts alone
  discriminate. No forbidden calls.
- Weights 0.3/0.7. Mute 0.300, nocall 0.000, fabricate n/a.

## The wrong answer

`/tmp/ext/scratch/162/wrong.md` picks "Red Hat OpenShift AI Workshop (`rhoai.datasci-workshop`) ...
built for workshops", with the decoy's UUID. It scores **0.30** (tool calls only).

Honest answers `honest1.md` (prose), `honest2.md` (a table, explicitly rejecting the Workshop item as
`multiuser: false`) and `honest3.md` ("supports multi-user provisioning") all score **1.000**.

## Invented

The cluster names `avocet` and `curlew`, the catalog item names, the display names, the UUIDs and the
keywords are all invented. `babylon-catalog-prod` is parsec's real catalog namespace. Nothing comes
from bench-v4, from the original bench-v5 or from production data.
