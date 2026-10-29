## What it measures

Arithmetic over a MultiWorkshop event's own workshops, where membership has to be worked out. The event lead's namespace on `heron` holds two MultiWorkshops and five Workshops:

- the event `ocp-dev-summit-oct26`, with `number_seats` 90 and three `assets`
- a Partner Bootcamp with one asset
- a standalone `ods-security-preview`, whose display name is "Developer Summit - Security Preview", which belongs to neither event

`list_workshops` does **not** project `multiworkshop`, so the agent can tell which workshops belong to the event only from `list_multiworkshops`' `assets[]`. It then has to:

- sum `user_count` over the three event workshops: 85, which is 5 short of 90
- sum `provision_count.active`: 82
- name `ods-serverless` (3 failed) as the weak spot

## Grounding

- platform SKILL.md `/query_babylon_catalog`:
  - `list_multiworkshops` reads `babylon_multiworkshops` by `cluster` and then `namespace`, projected to `name, namespace, display_name, number_seats, start_date, end_date, purpose, assets, asset_count`.
  - `list_workshops` reads `babylon_workshops` by `cluster` and `namespace`, projected to exactly `name, namespace, catalog_item, workshop_id, display_name, description, open_registration, lifespan, provision_count, user_count, user_assignments_count, resource_claims_count`.
  - "Never: ... include `multiworkshop` in list elements or outside `get_workshop`."
  - api.json: "Call list_multiworkshops alongside list_workshops, not instead of it."
- Constraints are honoured: `user_assignments_count <= user_count`, and `asset_count = length(assets)`.
- `cluster` is a free request string, and every row carries `cluster` and `namespace`. A same-named `ods-serverless` workshop in another user's namespace (60 users) cannot reach this namespace's listing.

## Contract

- Calls, `unordered-subset`: both listings pinned on `cluster` and `namespace` (both given in the instruction).
- Required: the weak workshop, `ods-serverless`.
- Counts: 85 user slots, 5 seats short (`derived`), 82 active environments.
- Forbidden fact `standalone-included`: the 105/145 slot totals, 102/142 active, and "covers all 90". It has no excuses; an honest answer never states those totals.
- Weights 0.3/0.7.

## The wrong answer

`.scratch/probe/132-wrong.md` counts ods-security-preview as part of the event (105 users, "covers all 90", 102 active). It scores **0.44** with the golden calls: three counts missed and the forbidden fact hit.

## Invented

The event names, workshop names and ids, seat counts, dates, emails and the cluster `heron` are invented. Nothing comes from bench-v4 or production data.
