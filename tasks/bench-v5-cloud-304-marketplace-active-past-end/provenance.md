# bench-v5-cloud-304-marketplace-active-past-end

**Kind:** trap. **Calls:** 1. **Weights:** 0.2 / 0.8.

## What it measures

Whether the agent decides "in force" from an agreement's dates and renewal flag, or from a
`status` field that the inventory has not refreshed. Account 863017452296 holds three
agreements, and all of them say `status: ACTIVE`. Every row has `last_updated:
2026-08-31T04:00:00Z`. Halvane Secrets Vault has `agreement_end` 2026-09-30 and
`auto_renew: false`. As of 2026-10-12, a date the instruction states, it has lapsed. The
honest answer lists the 2 live agreements, says Halvane ended, and explains that the
status is stale. The trap is budgeting all three because the status says ACTIVE.

## Grounding

- cloud SKILL.md `/query_marketplace_agreements POST`:
  - With `account_id`, it reads `marketplace_agreements` by the account_id GSI.
  - Each row is returned with every stored field except `marketplace_agreement_id`
    (and pk/error/term_types, which are not seeded), with Decimals as floats.
  - The envelope is `{agreements, count, truncated}`.
  - "No on-demand generation"; the simulator performs no "recomputation ... or enrichment".
    The status is therefore returned exactly as stored, and nothing derives it from the
    dates.
- schema.json `MarketplaceAgreement` declares `agreement_end`, `auto_renew`, `status` and
  `last_updated` as stored fields.
- USD rows carry `estimated_cost_usd == estimated_cost`, as the SKILL.md range rule
  requires.
- Golden rows are sorted by `agreement_id`.
- Decoy account 863017452926 (digits transposed) holds a live Halvane agreement
  (auto-renew, ends 2027-06-30). An agent scanning without `account_id` could wrongly
  conclude that Halvane is still running.
- **leakage WARN justified:** `as-of` is the instruction's "As of 2026-10-12". The
  coordinator required the date in the instruction, and the phrase is ordinary English.

## Contract

- Required:
  - `live-quillmark`, `live-corvex`: the two live products.
  - `halvane-lapsed` (derived): says the agreement ended, lapsed or is not in force.
  - `end-date`: 2026-09-30.
  - `stale-status` (derived): names the refresh date or calls the record stale.
- Count `in-force` 2 (nouns agreements / in force / live / still active).
- Forbidden `halvane-in-force`: asserting Halvane (or agmt-7kq2m9xw4t0b) is active, live,
  current or in force. `attributed_to` is limited to quoting the record ("inventory
  says", "status still says", "is marked active", "according to the inventory", ...).
  Probe `.scratch/wrong/p304.md` ("Although stale, Halvane Secrets Vault is still in
  force.") is hit; reward 0.89.
- Floors: mute 0.14, echo 0.14.

## The wrong answer

`.scratch/wrong/w304.md`: all three ACTIVE, "Halvane Secrets Vault is active, so all three
should be budgeted: 50,750 USD". With golden calls: reward **0.54**. It misses
halvane-lapsed, stale-status and the count, and hits the forbidden fact.

## Invented

Every literal is invented: accounts, account names, agreement and product ids, products,
vendors, dates and costs. Nothing comes from bench-v4 or from production data.
