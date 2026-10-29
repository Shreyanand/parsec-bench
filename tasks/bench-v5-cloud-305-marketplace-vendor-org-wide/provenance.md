# bench-v5-cloud-305-marketplace-vendor-org-wide

**Kind:** happy. **Calls:** 1. **Weights:** 0.2 / 0.8.

## What it measures

An org-wide question about one vendor, answered from the marketplace inventory's scan path
(no `account_id`), and then aggregated. The agent has to find all three Brightmoor
Analytics agreements on three accounts, say which one auto-renews, and add up their
estimated cost (23,955 USD), a figure no stored field holds. There is no trap. The
difficulty is completeness: covering every account rather than stopping at the first, and
doing the sum correctly.

## Grounding

- cloud SKILL.md `/query_marketplace_agreements POST`:
  - Without `account_id`, it scans `marketplace_agreements`.
  - `vendor_name` is a case-insensitive substring match applied client-side.
  - Rows are returned minus `marketplace_agreement_id`, with Decimals as floats.
  - The envelope is `{agreements, count, truncated}`.
- The golden call uses `vendor_name: "Brightmoor"`, and rows are sorted by `agreement_id`.
  No argument is pinned, because an unfiltered scan (6 rows) followed by reading the
  vendor column is equally honest.
- Seed: 3 Brightmoor rows (accounts 391774208516, 391774208562, 457102938841) plus 3 rows
  from two other vendors. One of those sits on a Brightmoor account (391774208516), and
  another on a fourth account. All rows are USD with `estimated_cost_usd ==
  estimated_cost`.

## Contract

- Required:
  - `acct-391774208516`, `acct-391774208562`, `acct-457102938841`: the three accounts.
  - `auto-renew-one` (derived): exactly one auto-renews.
  - `renewing-agreement`: names that agreement or its account name.
  - `total` (derived): 23,955.
- Count `agreement-count` 3 (nouns agreements / contracts / subscriptions). The wrong
  scopes give 6 (everything) or 2 (one product).
- No forbidden fact (happy path). Mute 0.00, echo 0.00.

## The wrong answer

`.scratch/wrong/w305.md`: it stops at the two Query Accelerator agreements and says both
auto-renew (19,830 USD). With golden calls: reward **0.43**. It misses the third account,
auto-renew-one, renewing-agreement, total and the count.

## Invented

Every literal is invented: accounts, account names, agreement and product ids, products,
vendors, dates and costs. Nothing comes from bench-v4 or from production data.
