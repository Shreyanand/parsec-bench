## What it measures

A join across two independent listings: does each workshop's `catalog_item` still exist in the
catalog? Two sibling calls on `siskin`:

1. `list_workshops {cluster: siskin, namespace: user-mbaptiste-redhat-com}` returns four workshops
   with their `catalog_item` values (`<ci_name>.<stage>`).
2. `search_catalog {cluster: siskin}` returns the published items as `ci_name` (stage suffix
   stripped) plus `stage`.

The agent has to rebuild `ci_name + "." + stage` and compare names exactly. Three workshops resolve:

- `edge-ai.camera-lab.prod`;
- `ocp.image-builds-lab.prod`;
- `aap.rulebook-first-steps.prod`, whose catalog **display name changed** to "EDA Rulebook Starter".
  Matching by display name wrongly calls it gone.

One workshop does not resolve: `rhel-compliance-dec` (code p8dtj) was built from
`rhel-sec.compliance-lab.prod`. siskin publishes only `rhel-sec.compliance-lab-v2`, and a prefix or
substring match wrongly calls that a hit. The original `rhel-sec.compliance-lab` exists only on
another cluster, `linnet`.

Answer: 3 of 4 are fine, `rhel-compliance-dec` / p8dtj is not.

Behaviour, for the authors of 165-169: **workshop `catalog_item` joined against `search_catalog`
`ci_name`+`stage`; the absence is hidden by a `-v2` near-name, with a display-name rename as the
opposite lure.** One count (still-fine workshops).

## Grounding

- platform SKILL.md `/query_babylon_catalog`: `list_workshops` reads `babylon_workshops` filtered by
  `cluster`, requires `namespace`, and projects `catalog_item`, `workshop_id` and the rest. The api.json
  STORE AUTHORITY paragraph says the same. `search_catalog` reads `babylon_catalog_items` filtered
  by `cluster`.
- `schema.json`: `ci_name` is "Catalog item name with recognized stage suffix removed". parsec splits
  the CatalogItem name at its last `.` when the suffix is `prod`/`dev`/`event`/`test`
  (`vendor/parsec/src/tools/babylon.py:122-133`). The workshop label carries the full name, so
  `ci_name + "." + stage` is the join key.
- Both golden calls are unfiltered and in name order. `search` is not pinned (hazard 19): searching
  "compliance" returns only the `-v2` row, which is the same trap. The calls are independent, so the
  match is `unordered-subset`.
- The workshops have not provisioned yet (`provision_count` zeros, no claims). Nothing graded
  depends on that.

## Contract

- Calls: `list_workshops {cluster, namespace}` and `search_catalog {cluster}`, unordered.
- Required: the broken workshop (`rhel-compliance-dec` or its display name) and its workshop ID
  `p8dtj`.
- Count: 3 still fine, with nouns workshops/fine/published and pair forms "3 of 4", "three of the
  four", "all but one".
- No forbidden facts: the decoy names are seed literals (hazard 14). No forbidden calls.
- Weights 0.3/0.7. Mute 0.300, nocall 0.000, fabricate n/a.

## The wrong answer

`/tmp/ext/scratch/164/wrong.md`, the substring matcher: "All four ... rhel-sec.compliance-lab (as
rhel-sec.compliance-lab-v2) ... nobody needs a warning". It scores **0.30**.

`wrong2.md`, the display-name matcher, flags both rulebook-steps-dec and rhel-compliance-dec. It
scores **0.767**, because it states the true broken workshop and its code (bar C residual).

The extra form "all but one" carries a residual of its own. An answer that says "all but one" but
names the wrong workshop banks the count.

Honest answers `honest1.md` (prose) and `honest2.md` (a table plus Key: value, explicitly ruling out
`-v2` and the renamed display name) both score **1.000**.

## Invented

The clusters `siskin` and `linnet`, the namespace, the workshop names and codes, the catalog item
names, the display names and the UUIDs are all invented. `babylon-catalog-prod` is parsec's real
namespace. Nothing comes from bench-v4, from the original bench-v5 or from production data.
