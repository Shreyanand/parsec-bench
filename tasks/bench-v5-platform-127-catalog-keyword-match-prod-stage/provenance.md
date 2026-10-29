## What it measures

One `query_babylon_catalog` `search_catalog` call on `puffin`. The user wants a production-stage service mesh lab. A search for "service mesh" (or "mesh", or "istio") returns two items, and the obvious one is the wrong one:

- `netsvc.mesh-deep-dive`, "Service Mesh Deep Dive": a title match, but `stage: dev` in `babylon-catalog-dev`.
- `netsvc.traffic-mgmt-lab`, "OpenShift Traffic Management Lab": `stage: prod`. It matches **only through `keywords`** ("service mesh", "istio", ...); neither its display name nor its ci_name says mesh.

The agent has to read `stage` and the keyword match, not just the title.

## Grounding

- platform SKILL.md `/query_babylon_catalog`: `search_catalog` reads `babylon_catalog_items` filtered by `cluster`. `search` is a "case-insensitive substring over `ci_name`, `display_name`, `keywords`". Items are projected to `ci_name, display_name, namespace, stage, multiuser, asset_uuid, keywords`. `namespace` is not a filter.
- `cluster` is a free string in the request schema, and every seeded row carries `cluster`. kite holds a **prod** twin of `netsvc.mesh-deep-dive`. Cluster filtering means a puffin search can never return it; it exists so that "the deep dive is prod somewhere" stays an off-cluster fact. Its UUID is forbidden as an order value.
- `total_scanned` is 5: the puffin rows before truncation.

## Contract

- Call: `search_catalog` with `cluster: puffin`. `search` is unpinned, so any reasonable term works, and so does listing the whole puffin catalog.
- Required: the prod item (ci_name or display name), its asset UUID, that the title match is dev stage, and that the prod item is single-user (`multiuser: false`), which answers the instruction's sharing question.
- Forbidden facts:
  - `recommend-dev-item`: ordering, using or recommending the Deep Dive, or quoting either Deep Dive UUID. The `attributed_to` phrases are specific refusals ("do not order", "would not use", "not suitable", "not production", ...). Probed: "Order the Service Mesh Deep Dive, but it is dev stage." still hits. "I would not use the Service Mesh Deep Dive because it is dev stage" is excused (0.72).
- Weights 0.3/0.7.

## The wrong answer

`.scratch/probe/127-wrong.md`: "order the Service Mesh Deep Dive ... UUID b83f2d6e-..." scores **0.30** with the golden calls (answer 0/5: forbidden hit, all four required facts missed). Mute floor 0.20 (0.44 with golden calls). A second forbidden fact ("no production lab exists") was dropped to keep the floor under 0.45.

## Invented

All catalog names, display names, UUIDs, keywords and the clusters `puffin`/`kite` are invented. Nothing comes from bench-v4 or production data.
