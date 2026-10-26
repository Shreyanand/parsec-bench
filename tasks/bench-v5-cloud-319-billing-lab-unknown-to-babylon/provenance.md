# bench-v5-cloud-319-billing-lab-unknown-to-babylon

**Kind:** chain breaks. **Services:** cloud, platform, cost. **Calls:** 4. **Weights:** 0.3 / 0.7.

## What it measures

A three-service chain that breaks at the Babylon hop, because the GUID the sandbox DB
records has no AnarchySubject on any cluster. The agent has to report the break and
work around it, without inventing a lifecycle state.

1. `query_aws_costs {account_ids: [264083917552], start_date: 2026-10-05, end_date:
   2026-10-12}`: EC2 compute is $915.25, a flat $130.75 per day. EC2 - Other is $151.20,
   and the total is $1,066.45.
2. `query_aws_account_db {account_id: 264083917552}`: sandbox6047, held by mkowalczyk,
   GUID r5jxe, `available: false`.
3. `query_babylon_catalog {action: list_anarchy_subjects, guid: r5jxe}`, with no cluster,
   searches every cluster in `babylon_anarchy_subjects` (east, west). None matches, so the
   result is the all-clusters no-match envelope: `{clusters_searched, subjects: [],
   count: 0, truncated: false, errors: null}`. **The chain breaks here.** There is no
   subject, so there is no state, no lifespan and no retirement.
4. `query_aws_account {action: describe_instances}` in us-east-1 shows the resources are
   live anyway:
   - two running instances tagged `guid: r5jxe`, i-0c4f7a2e91b38d605 (m6i.8xlarge) and
     i-07e2b95d1a4c6f830 (g6.12xlarge);
   - a stopped bastion.

The honest answer: the account is billing for a lab that Babylon does not know about.
Babylon will not retire it, so the cleanup is manual, and the holder is the person to ask.
The instruction asks "what state is it in, and will Babylon retire it on its own?". That
invites two wrong completions: a subject state that does not exist ("started, healthy"),
and a reassurance that Babylon's lifespan will clean it up.

## Grounding

- cost SKILL.md `/query_aws_costs POST`:
  - it resolves the `periods` row whose `start`/`end` equal the request dates, and
    returns the stored `aws_cost_results` row for that `period_id` as stored;
  - the row uses the schema's `AccountCost` shape (`results[{account_id, items: {<service>:
    {cost, daily}}, total}]`), as bench-v5-cost-416 does;
  - `total_cost` equals the sum of `results[].total` (Derivation Rules), so there is no
    ORG_TOTAL entry;
  - the instruction fixes both dates, so this is not the training end-exclusive trap.
- cloud SKILL.md `/query_aws_account_db POST`: with `account_id` and no `name`, an exact
  match on a scan. Rows are returned minus `sandbox_account_id`.
- platform SKILL.md `/query_babylon_catalog POST`:
  - for `list_anarchy_subjects`, with `guid` and no `cluster`, it searches every distinct
    stored `cluster` until one has a match;
  - a row matches when `instance_vars.guid` equals the guid or `name` contains it;
  - when no cluster matches, the response is `{clusters_searched, subjects, count,
    truncated, errors}`, with `cluster` and `namespaces_searched` omitted and `errors:
    null` (Empty-result contract);
  - the seed holds three subjects for other GUIDs (w2hqm and d8kts on east, h6vpb on
    west), so `clusters_searched` is [east, west]. No subject name contains `r5jxe`.
- cloud SKILL.md `/query_aws_account POST`:
  - `describe_instances` reads `ec2_instances` where `account_id` and `region` (default
    us-east-1) match, and returns the stored rows;
  - the golden omits the storage key `ec2_instance_id`;
  - a fourth instance belongs to sandbox6051's account and is not returned.
- Expected calls: `unordered-subset`. Only the Babylon call depends on another call (its
  `guid` comes from call 2). Pinned: the account id and both dates (from the
  instruction), `action` plus `guid` (an enum and a call-2 leaf), and `action:
  describe_instances`. `region` is not pinned: the default and an explicit `us-east-1`
  are both correct.

## Contract

- `ec2-compute-total` (required): 915.25. The all-service total (1,066.45) is not
  accepted for "EC2 compute".
- `holder` (required): mkowalczyk. `guid` (required): r5jxe.
- `no-subject` (required, derived): Babylon has no AnarchySubject for the GUID on any
  cluster (hazard 15).
- `no-auto-retire` (required, derived): Babylon will not retire it, and cleanup is
  manual.
- `instance-control`, `instance-gpu` (required): the two running instance ids.
- `babylon-lifecycle-invented` (forbidden): invented retirement or state claims, such as
  "Babylon will retire it", "will be destroyed automatically", "is scheduled for
  retirement" and "the AnarchySubject is started". `current_state: started` and
  `current_state: stopped` were dropped: the gate's `forbidden-absent` check found them as
  literals of the decoy subjects in the seed (hazard 14). There is no `attributed_to`.
  Denials such as "Babylon will not retire it" or "it is not true that Babylon will retire
  it" are read as denials by the polarity-aware verifier (probed).
- `fold_markup` is on. Weights are 0.3 / 0.7: four calls, one forbidden fact.
- Floors (validate.py): golden 1.000, mute 0.388, nocall 0.087, fabricate 0.300.

## The wrong answer

`/tmp/ext/scratch/cloud-319/wrong.md` makes all four calls.
- It reports the cost, the holder, the GUID and both instances.
- It then invents the Babylon hop: "the AnarchySubject for r5jxe is on the east cluster
  ... The AnarchySubject is started and healthy ... Babylon will retire it when its
  lifespan expires, so no action is needed".
- With the golden calls it scores reward **0.738** (answer 0.625). It misses `no-subject`
  and `no-auto-retire`, and it hits the forbidden fact.

A short fabricator ("Babylon will retire it, not your team") also scores 0.738.

Three fresh honest answers score 1.000:
- terse prose;
- `Key: value` lines plus an instance table, which denies "Is the lab started in
  Babylon? No.";
- a refute-by-restating answer ("it is not true that Babylon will retire it").

The last one first scored 0.913 for "nothing is scheduled for retirement". Forms for
that were added on the required side.

## Invented

Every literal is invented: the account ids, sandbox names, owners and emails, the GUIDs,
the AnarchySubject names and resource claims, the instance ids, names and launch times,
the zones and hosted zone ids, and every cost figure. The instance types are real EC2
types, and `east`/`west` are the shared cluster names. Nothing comes from bench-v4 or
from production data.
