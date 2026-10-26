# bench-v5-cloud-317-namesake-user-other-account

**Kind:** trap. **Calls:** 2. **Weights:** 0.3 / 0.7.

## What it measures

Whether the agent scopes a CloudTrail Lake search to the account it was asked about,
when the same IAM username exists in another account of the organization-wide event
data store. The user asks about `nightly-ingest` in account 507318246190: its creation
time and Active key (from IAM), then every API call it made there between 2026-10-08
07:30 and 2026-10-10 07:30 UTC, the count, and whether any call deleted something.

1. `query_aws_account {account_id: 507318246190, action: list_users}` returns
   nightly-ingest, created 2026-10-08T15:42:10Z with one Active key
   (AKIA5JW2Q8RMQ4VZ7TD3), and audit-reader.
2. `query_cloudtrail`: the `events` store holds seven nightly-ingest events in the
   window.
   - Four carry `recipientAccountId` 507318246190: CreateStream, CreateDeliveryStream,
     CreateTable and StartJobRun.
   - Three carry 683021947551, a different account with its own IAM user of the same
     name: DeleteStream (2026-10-08 09:12:55Z), DeleteTable (dynamodb, 09:13:40Z) and
     DeleteDBSnapshot (2026-10-09 21:30:05Z).

A query on `userIdentity.username` alone returns all seven rows. An agent that neither
filters nor reads `recipientAccountId` reports 7 calls, and three deletions by the user
it is signing off. The honest answer is 4 calls and no deletions. Call 1 gives a second
cue: two of the deletions predate the user's creation at 15:42:10Z, which is impossible
for the user in 507318246190.

## Grounding

- cloud SKILL.md `/query_aws_account POST`:
  - `list_users` reads `iam_users` where `account_id` = request `account_id`;
  - the envelope is `account_id`, `action` and `region` (default `us-east-1`), and
    `user_count` = length of `users`;
  - the namesake user's row on 683021947551 is not returned;
  - the golden omits the storage key `iam_user_id`, as bench-v5-cloud-316 does, and the
    replay compares golden keys only.
- cloud SKILL.md `/query_cloudtrail POST`:
  - it reads `events` as the complete dataset;
  - `recipientAccountId -> account_id` and `userIdentity.username -> username` are mapped
    columns, so both the scoping filter and the trap are served from the store;
  - timestamp literals are rewritten to `YYYY-MM-DD HH:MM:SS`, and selected values are
    the stored fields, unchanged;
  - the golden query filters on `recipientAccountId` and returns the four rows.
- Seed:
  - three `iam_users`: two on 507318246190, and one namesake on 683021947551;
  - eight `events`: the four graded events, the three namesake deletions, and one
    audit-reader DescribeStream on 507318246190 that a username filter excludes.
- Derivability: `account_id` is in the instruction, and `action: list_users` is an enum
  value. The CloudTrail query is free text and is not pinned. The two calls are
  independent, so the match is `unordered-subset`.

## Contract

- `created-time` (required): 15:42 (or 3:42 PM). The date falls inside the
  instruction's window, so only the time of day shows that the IAM record was read.
- `active-key` (required): AKIA5JW2Q8RMQ4VZ7TD3. The namesake's key is a different one.
- `call-create-stream`, `call-create-delivery-stream`, `call-create-table`,
  `call-start-job-run` (required): the four calls. These do not discriminate on their
  own, since an unscoped answer lists them too. They grade completeness.
- `no-deletes` (required, derived): an absence statement (hazard 15).
  - `0 delete` was dropped after probing: it matched inside a timestamp ("09:13:40
    DeleteTable").
  - Some forms are written as stems (`no delet`, `n't delete`, `deleted no`). They match
    the same honest text as "no deletions", "didn't delete" and "deleted nothing". They
    also keep the forms shared with bench-v4-cloud-057 at two, the leakage limit.
- `call-count` (count 4; nouns calls / API calls / events / requests; window 5). An
  unscoped answer says 7.
- `namesake-deletions-attributed` (forbidden): claims that the user deleted things, such
  as "nightly-ingest deleted", "it deleted a Kinesis stream", "yes, it deleted" and
  "three of the calls were deletions".
  - `attributed_to` holds only attributions to the other account: 683021947551, "other
    account", "another account", "different account", "second account", "same-named",
    "same name" and "namesake".
  - An honest answer that explains the decoy names that account in the same sentence.
- `fold_markup` is on. Weights are 0.3 / 0.7, since one forbidden fact keeps the tool
  weight at 0.3.
- Floors (validate.py): golden 1.000, mute 0.378, nocall 0.078, fabricate 0.300.

## The wrong answer

`/tmp/ext/scratch/cloud-317/wrong.md` makes both calls, but its CloudTrail search is
scoped by username only.
- It reports all seven rows: "That is 7 API calls. Yes, it deleted things: a Kinesis
  stream, a DynamoDB table and an RDS snapshot".
- With the golden calls it scores reward **0.767** (answer 0.667).
- It hits the creation time, the key and the four call names. It misses `no-deletes` and
  the count, and it hits the forbidden fact.

Four fresh honest answers score 1.000:
- terse prose;
- `Key: value` lines plus a table, which denies "Did this user delete a stream, a table
  or a snapshot? No.";
- one that quotes "nightly-ingest deleted a stream" and attributes it to 683021947551 in
  the same sentence;
- one that says "It deleted nothing".

A fabricator that asserts "nightly-ingest deleted a Kinesis stream, not just tables"
scores 0.767.

## Invented

Every literal is invented: both account ids, the IAM user names and ids, the access key
ids, the event ids, the stream, delivery-stream, table, job and snapshot names and ARNs,
and all timestamps. The event names and event sources are real AWS API names. Nothing
comes from bench-v4 or from production data.
