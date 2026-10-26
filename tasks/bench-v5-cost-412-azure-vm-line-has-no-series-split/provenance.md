# bench-v5-cost-412-azure-vm-line-has-no-series-split

## What it measures

Whether the agent notices that a breakdown it was asked for is empty, and that a derived
field built from that breakdown is therefore uninformative. Finance wants subscription
`pool-58-064`'s Virtual Machines line for 2026-09-14..2026-09-27 itemised by VM series,
plus the GPU share. `query_azure_costs` (cache path, refreshed 2026-09-28, so the data is
current) returns Virtual Machines at $9,264.80 with **`meter_subcategories: {}`**. Parsec
adds no key for a billing row whose MeterSubCategory is empty. Storage and Bandwidth
beside it have populated maps. `gpu_cost` is 0.0. Parsec computes it by a substring test
for NC/ND/NV on the meter subcategory, so with no subcategories on the VM rows the test
cannot fire, and 0.0 measures nothing. The honest answer gives $9,264.80 and the
$10,720.87 total, says no series split exists, and says the GPU share cannot be
determined. The trap is to read `gpu_cost: 0.0` as "the pilot used no GPUs". A render-farm
pilot makes that an expensive reading.

## Grounding

- `api.json` AzureServiceCost.meter_subcategories: "A billing row whose MeterSubCategory
  is empty contributes no key at all ..., so this object is always present but may be
  empty". AzureSubscriptionCost.gpu_cost: "The test is a substring match for NC, ND or NV
  against the upper-cased subcategory".
- SKILL.md `/query_azure_costs POST`: `azure_cost_results` is non-empty, so the cache path
  is taken. `periods` resolves 2026-09-14/2026-09-27 to `per-az-q2x-0927`, and the stored
  row is returned exactly as stored. Derivation rules: `gpu_cost` and `AzureServiceCost.cost`
  are "never recomputed", so the simulation cannot fill the map or recompute the zero. The
  rows are mirrored in `azure_service_costs` and `azure_subscription_costs`, as the
  siblings do.
- No seeded subcategory contains NC/ND/NV ("Premium SSD v2 Disks", "Hot LRS Block Blob",
  "Inter-Region"), so `gpu_cost` 0.0 is exactly what parsec computes (the generator
  asserts this). Each populated map sums to its service cost. `cache_last_refresh`
  (2026-09-28T05:20:00Z) is after the window, so no freshness caveat is in play
  (contrast 405).

## Contract

- Expected call (unordered-subset): `query_azure_costs` for `pool-58-064`, 2026-09-14 to
  2026-09-27.
- `no-series-split` (required, derived): the VM series breakdown is empty or unavailable.
- `gpu-share-unknown` (required, derived): the GPU portion cannot be determined, or the 0.0
  is not evidence of zero GPU. Every form is anchored on "gpu", so a series-only refusal
  cannot earn it.
- Counts: `vm-total` $9,264.80 and `subscription-total` $10,720.87.
- `zero-gpu-asserted` (forbidden): asserting claims such as "GPU cost was $0", "there was
  no GPU spend", "pilot used no GPU", or "was all non-GPU". It carries no `attributed_to`.
  A refutation like "doesn't mean there was no GPU spend" is excused by the verifier's
  polarity reading (checked with honest answers).
- Weights 0.3/0.7.

## The wrong answer

"For pool-58-064 from 2026-09-14 to 2026-09-27, Virtual Machines cost $9,264.80 and the
subscription total was $10,720.87. The VM series split didn't come through in the result.
GPU cost was $0 (gpu_cost 0.0), so the render farm ran on CPU instances only." With the
golden calls this scores 0.3 + 0.7 x 2/5 = 0.58 (`score_answer.py`). It keeps both counts,
misses both required facts (its series remark matches no form) and hits the forbidden one.
The content-free answer scores 0.44.

## Invented

Every literal is invented: the subscription, all meter figures, the refresh timestamp and
the storage ids. Nothing comes from bench-v4 or from production data.
