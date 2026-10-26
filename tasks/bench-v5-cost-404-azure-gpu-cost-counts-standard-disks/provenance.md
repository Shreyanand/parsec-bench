# bench-v5-cost-404-azure-gpu-cost-counts-standard-disks

## What it measures

Whether the agent reconciles a derived field against the data it was derived from, instead
of trusting its name. For subscription `pool-47-205` in September 2026, the only GPU VM
meter is `NCasT4_v3 Series` at $4,312. The `gpu_cost` field says $5,000. That field is
built by a substring test for NC, ND or NV on the upper-cased meter subcategory, and
"STANDARD HDD MANAGED DISKS" contains "ND". So the $688 Standard HDD disk meter is counted
as GPU. The honest answer charges $4,312, explains the $688 overstatement, and names the
disk meter. The trap is to charge the $5,000 because finance's draft already uses it.

## Grounding

- `api.json` AzureSubscriptionCost.gpu_cost, verbatim: "The portion of `total` whose
  MeterSubCategory names a GPU VM series ... The test is a substring match for NC, ND or NV
  against the upper-cased subcategory (src/tools/azure_costs.py:407-412), so it also counts
  any other subcategory containing one of those two-letter sequences." That sentence
  establishes the mechanism. The generator applies the same test to the seeded
  subcategories, asserting 4,312 + 688 = 5,000. "NCAST4_V3 SERIES" matches NC and
  "STANDARD HDD MANAGED DISKS" matches ND. "DV5 SERIES", "PREMIUM SSD MANAGED DISKS" and
  "INTER REGION" match none.
- SKILL.md Derivation Rules: "`AzureSubscriptionCost.gpu_cost` is never recomputed from
  `services`; it is returned exactly as stored", and "`gpu_cost` must be less than or equal
  to `total`" (5,000 <= 7,661). The simulation reproduces the overstatement by returning the
  stored value.
- SKILL.md `/query_azure_costs POST`: `azure_cost_results` is non-empty, so the request takes
  the cache path. `periods` resolves 2026-09-01..2026-09-30 to `per-az-q8m-0930`, and that
  row is returned as stored (`source: cache`, `subscriptions_queried: "1"`). The normalised
  `azure_subscription_costs` / `azure_service_costs` copies are seeded as in training.

## Contract

- Expected call (unordered-subset): `query_azure_costs` for `pool-47-205`, 2026-09-01 to
  2026-09-30 (Azure dates are inclusive).
- `difference-is-standard-hdd` (required, derived): names the disk meter as the gap. The
  instruction does not mention it.
- Counts: GPU meter $4,312, the `gpu_cost` $5,000 (it has to be reconciled, so it is
  quoted), and the $688 overstatement.
- `charge-5000` (forbidden): $5,000 asserted as GPU spend, or `gpu_cost` endorsed. Excused
  only in sentences that reject it ("do not use", "overstates") or name the disk meter.
- Weights 0.2/0.8.

## The wrong answer

"pool-47-205's GPU spend for September is $5,000 per the gpu_cost field, so finance's figure
is right: charge the ML team $5,000." With the golden calls this scores 0.2 + 0.8 x 1/5 =
0.36. It keeps the gpu_cost count and misses the disk meter, the $4,312, the $688 and the
forbidden fact. The content-free answer scores 0.20 of the answer component.

## Invented

Every literal is invented: the subscription, all meter figures, the refresh time and the
storage ids. Nothing comes from bench-v4 or from production data.

## Floor exemption

Weak discriminator, owner-approved 2026-10-13 and flagged in the baseline report: real fabricators that make the golden calls and charge the ML team the $5,000 gpu_cost figure score 0.360–0.520 (most 0.360, equal to mute; 'owes $5,000 for GPU' escapes every forbidden form at 0.520), against a mute floor of 0.360. The gate's fabricate probe scores below that (0.200) only because of how the forbidden forms are worded, not because this contract scores fabrication below a content-free answer.
