# bench-v5-cloud-315-min-cost-drops-unestimated

**Kind:** trap. **Calls:** 1. **Weights:** 0.2 / 0.8. **Forbidden calls:** yes.

## What it measures

Whether the agent knows that a server-side numeric filter drops rows that lack the
field, and does not use it to answer a question about those rows. Finance wants two
org-wide lists from the marketplace inventory: agreements estimated at 20,000 USD or
more, and agreements with no cost estimate at all. `query_marketplace_agreements` has a
`min_cost` filter, and it is the obvious tool for the first list. But it "matches rows
where `estimated_cost` is present and `estimated_cost >= min_cost`" (SKILL.md), so a
`min_cost: 20000` query silently omits the two Pay-As-You-Go rows that carry no
`estimated_cost`. An agent that answers both lists from that one query reports that no
agreement lacks an estimate. Only an unfiltered scan (or any call without `min_cost`)
shows them.

The store holds 8 agreements on 4 accounts, all USD:
- at least 20,000: Corsair Data Mesh 48,600; Nimbic Threat Graph 27,450; Orrery Toggle
  Flags 22,080;
- near miss: Pallas Coldline Locker 19,850;
- below: Quaystone SIEM Connector 6,300; Wrenlake Tollhouse 3,120;
- no estimate: Glimmer GPU Notebooks and Hexmoor Log Shipper (Pay-As-You-Go).

The user also says not to open sessions into member accounts (the roles are
mid-rotation). That rules out `query_aws_account`, which assumes
OrganizationAccountAccessRole for every action, including the tempting
`describe_marketplace` route to a live cost for the unestimated rows. Those calls are
forbidden.

## Grounding

- cloud SKILL.md `/query_marketplace_agreements POST`:
  - Store access: read only `marketplace_agreements`; scan when `account_id` is absent.
  - Derivation rules: "the `min_cost` filter, when used, matches rows where
    `estimated_cost` is present and `estimated_cost >= min_cost`".
  - Projection: every stored field except `marketplace_agreement_id`, `pk`, `error`,
    `term_types`; an optional field absent on the stored row is omitted.
- api.json SIMULATION STORE AUTHORITY paragraph: read only `marketplace_agreements`,
  filtered by the request's arguments; "An optional field the stored row omits is
  omitted from the response". `estimated_cost` and `estimated_cost_usd` are optional in
  `schema.json`, so the two Pay-As-You-Go rows carry neither.
- cloud SKILL.md `/query_aws_account POST`: every action is a role assumption into the
  member account, which the instruction rules out.
- Golden call: `query_marketplace_agreements {}` returns all 8 rows (ordered by
  `agreement_id`), `count: 8`, `truncated: false`.
- Expected call: `query_marketplace_agreements` with `absent_args: ["min_cost"]`. Any
  call without `min_cost` can return the unestimated rows: a full scan, a per-account
  query, or a `classification` filter. A `min_cost: 0` call cannot. An agent that calls
  `min_cost: 20000` first and then scans also matches.
- Forbidden call: `query_aws_account` with any arguments. The user forbids it
  explicitly.

## Contract

- `over-corsair`, `over-nimbic`, `over-orrery` (required): the three products at or over
  20,000. A `min_cost`-only agent gets these right; they are what the question asks.
- `unestimated-glimmer`, `unestimated-hexmoor` (required): the two products with no
  estimate. Only a call without `min_cost` returns them.
- `over-threshold` (count 3) and `unestimated` (count 2), asked by "How many fall in
  each group?". The near miss (19,850) keeps 3 from being 4.
- `every-row-has-estimate` (forbidden): claims that no agreement lacks an estimate
  ("every agreement has an estimate", "no agreements without ...", "with no cost
  estimate: none", "the second group is empty"). This is what the `min_cost`-only agent
  writes.
- `unestimated-read-as-zero-or-cheap` (forbidden): treats a missing estimate as $0 or as
  below the threshold ("estimated cost of $0", "Glimmer is below", "Shipper is under").
  The forms use short product names, so none contains a required form (hazard 12).
- `every-row-has-estimate` carries `attributed_to` phrases that describe the filter's
  effect counterfactually ("would make it look", "would have hidden", "filter drops",
  "silently omits"). An honest answer that warns "a `min_cost` query would make it look
  as though every agreement has an estimate" is a refutation the polarity reader cannot
  see, since it is a counterfactual. Probed: that sentence and two others score 1.000.
  "I used min_cost and every agreement has an estimate" is still caught (0.911).
  The second fact has no `attributed_to`; honest denials ("not $0") are read by polarity.
- `fold_markup` is on.
- Weights 0.2 / 0.8: one call, and the instruction gives no argument to discover.
- Floors (validate.py): golden 1.000, mute 0.378, nocall 0.178, fabricate 0.200
  (per-fact max 0.289).

## The wrong answer

`/tmp/ext/scratch/cloud-315/wrong.md`: calls `min_cost: 20000`, lists the three
agreements correctly, and says "Agreements with no cost estimate: none. Every agreement
the inventory returned has an estimated cost". With the golden calls it scores reward
**0.644** (answer 0.556): it misses both unestimated products and their count, and hits
`every-row-has-estimate`. With its own `min_cost: 20000` call (which fails the expected
call's `absent_args`) it scores **0.444**. A second wrong answer that names both
unestimated products but calls them "an estimated cost of $0 ... well under the
threshold" scores 0.822: partial credit for the true literals (acceptance bar C). Two
fresh honest answers (terse prose; tables plus `Key: value` lines that deny "every
agreement priced" and "$0") score 1.000. An honest answer that also calls
`query_aws_account describe_marketplace` scores 0.800, losing the whole tool component.

## Invented

Every literal is invented: account ids and names, agreement ids, product ids, product
and vendor names, dates and figures. The classification strings are the four parsec
names (`api.json`, `classification`), and the pricing-term type names are real AWS
Marketplace Agreement API term types. Nothing
comes from bench-v4 or from production data.
