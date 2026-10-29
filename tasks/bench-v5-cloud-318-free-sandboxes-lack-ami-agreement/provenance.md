# bench-v5-cloud-318-free-sandboxes-lack-ami-agreement

**Kind:** negative. **Calls:** 3. **Weights:** 0.3 / 0.7.

## What it measures

A readiness check whose finding is an empty join across two inventories. A four-seat
partner lab needs, per seat:
- one free AWS sandbox from reservation `tessellate-2611`;
- one free Azure subscription from pool 44;
- in that AWS account, an active Marketplace agreement for the Corvane Hardened
  Netwarden product, which the lab image needs before it can launch.

The three reads:

1. `query_aws_account_db {reservation: tessellate-2611}` returns six rows. Four are
   `available: true` (sandbox8521 to sandbox8524), exactly one per seat. Two (sandbox8525
   and sandbox8526) are held by rvashisht.
2. `query_marketplace_agreements` (for the product) returns four Corvane rows:
   - three ACTIVE, on sandbox8525, sandbox8526 and golden-images-shared;
   - one EXPIRED free trial, on sandbox8523 (ended 2026-10-09).
3. `query_azure_pools get_pool 44` shows 6 of 8 subscriptions free.

Sandboxes and Azure capacity are sufficient. The finding is a non-finding: **no free
sandbox holds an active agreement**, so the lab cannot run as planned.

There are two near-misses:
- reading "three ACTIVE agreements for the product" as "the product is subscribed",
  without joining on `account_id`;
- reading sandbox8523's EXPIRED trial as coverage.

sandbox8521 also carries an unrelated ACTIVE agreement (Quillstone Logweave). An agent
that checks only "does this account have any active agreement" gets that seat wrong.

## Grounding

- cloud SKILL.md `/query_aws_account_db POST`:
  - with no `name`, it does a collection scan;
  - `reservation` is a case-insensitive substring filter, and no other reservation in the
    seed contains `tessellate-2611` (sandbox8519 is `general`);
  - rows are returned minus `sandbox_account_id`.
- cloud SKILL.md `/query_marketplace_agreements POST`:
  - with no `account_id`, it scans; `product_name` is a client-side case-insensitive
    substring filter;
  - the projection drops `marketplace_agreement_id`, `pk`, `error` and `term_types`.
  - Per-account calls (`account_id` for each free sandbox) are an equally valid route.
    They return sandbox8523's EXPIRED row, sandbox8521's Quillstone row and nothing for
    the other two. Hence the expected call pins no argument (a product filter is free
    text, hazard 19).
- cloud SKILL.md `/query_azure_pools POST`:
  - `get_pool` reads rows whose `id` starts with `pool-44-` in the `pools` database;
  - `total` is the length of `subscriptions`, `in_use` counts `used: true`, and
    `available` = `total - in_use`;
  - `list_pools` gives the same 6 free for pool 44, so the expected call pins nothing;
  - pool 45 rows exist and are excluded by the prefix.
- Expected calls: `unordered-subset`, since all three are independent. Only
  `reservation` is pinned, and it comes from the instruction.

## Contract

- `free-8521` to `free-8524` (required): each free sandbox, by name or account id.
  Completeness. A wrong answer usually hits these.
- `pool-44-free` (required): 6 free of 8, or the first free id, `pool-44-103`. Kept as a
  required string rather than a count, to stay within the group's count budget.
- `expired-8523` (required): the near-miss row is not active. Forms: expired, no longer
  active, lapse, is not / isn't active, inactive, ended (2026-10-09). Only two forms
  ("expired", "no longer active") are shared with bench-v5-cloud-304, the leakage limit.
  "lapse" also matches "lapsed".
- `none-on-free` (required, derived): no free sandbox holds an active Corvane agreement.
  This is the negative finding (hazard 15). `| no |` was dropped after probing: it would
  credit a table that marks only some seats "no".
- `cannot-run` (required, derived): the bottom line.
- No counts and no forbidden facts. The group budget (about 8 forbidden facts and 7
  counts over cloud-311..319) was already met by cloud-311..317 and cloud-319. The wrong
  readings are graded by the derived facts they miss.
- `fold_markup` is on. Weights are 0.3 / 0.7, the slot's weights.
- Floors (validate.py): golden 1.000, mute 0.300, nocall 0.000, fabricate n/a (no
  forbidden fact).

## The wrong answer

`/tmp/ext/scratch/cloud-318/wrong.md` makes all three calls.
- It lists the four free sandboxes and the 6 free Azure subscriptions, then says "the
  Marketplace inventory has three ACTIVE agreements for the product ... so the image is
  subscribed and will launch. Yes, the lab can run as planned."
- With the golden calls it scores reward **0.738** (answer 0.625). It misses
  `expired-8523`, `none-on-free` and `cannot-run`.

A second wrong answer, `wrong2.md`, reads sandbox8523's expired trial as coverage ("1 of
4 seats can boot the image today"). It also scores 0.738.

Three fresh honest answers score 1.000:
- terse prose;
- `Key: value` lines plus a status table, which denies "Is sandbox8523 covered ...? No";
- one built on polar questions ("Do any of the free sandboxes hold an active ...
  agreement? No.").

The last one first scored 0.913. `agreement? no` and `agreement: none` were added on
the required side. Nothing was narrowed.

## Invented

Every literal is invented: the reservation `tessellate-2611`, the sandbox names, the
account ids, the zones and hosted zone ids, the owner, the GUIDs, the agreement and
product ids, the product and vendor names (Corvane Hardened Netwarden, Corvane
Securitech, Quillstone Logweave, Quillstone Ltd), golden-images-shared, the Azure
subscription ids and project tags, the costs and all dates. The term type names are
real AWS Marketplace term types. Nothing comes from bench-v4 or from production data.
