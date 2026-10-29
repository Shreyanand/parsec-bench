# bench-v5-cloud-316-cleaned-sandbox-live-iam-keys

**Kind:** trap. **Calls:** 2. **Weights:** 0.3 / 0.7.

## What it measures

Whether the agent checks a sandbox's cleanup flag against IAM, reading key status and
console use per user against a timestamp taken from the first call. The user hands
sandbox9174 to a workshop and states the pool's rule: a cleaned sandbox holds only the
rhdp-audit-ro IAM user, with no access keys.

1. `query_aws_account_db {name: sandbox9174}` returns account 318274950613, with
   `available: true`, `conan_status: clean` and the comment "conan cleanup completed
   2026-10-06T03:40:00Z".
2. `query_aws_account {account_id: 318274950613, action: list_users}` returns three
   users:
   - rhdp-audit-ro, with no keys (the expected baseline);
   - lab-admin-7rq2m, created 2026-09-26, with **two Active keys** and
     `password_last_used` 2026-10-07T09:12:40Z, a day *after* the cleanup;
   - ci-deployer, with one **Inactive** key and a console sign-in on 2026-09-30,
     *before* the cleanup.

The honest answer: two leftover users, 2 Active keys (both on lab-admin-7rq2m), a
console sign-in after cleanup, so not safe to hand over. There are two traps. The
first is to trust the green DB row ("conan says clean, available"). The second is to
read ci-deployer's Inactive key, or its pre-cleanup sign-in, as the whole picture. The
"since the cleanup" comparison needs the time from the DB comment (call 1) applied to
each user's `password_last_used` (call 2).

## Grounding

- cloud SKILL.md `/query_aws_account_db POST`: "When `name` is provided — Read
  `sandbox_accounts` by `name`"; each row is returned with every stored field except
  `sandbox_account_id`; the body is `{accounts, count, truncated}`.
- cloud SKILL.md `/query_aws_account POST`: `list_users` reads `iam_users` where
  `account_id` = request `account_id`; the envelope carries `account_id`, `action` and
  `region` (default `us-east-1`); `user_count` is the length of `users`. api.json:
  "Every element of ... `users` ... is the stored row, echoed with EVERY field the
  element's schema declares". The golden omits the storage key `iam_user_id`, following
  bench-v5-cloud-309. The replay compares golden keys only.
- Seed: two `sandbox_accounts` rows (sandbox9174 and an unrelated sandbox9182 on another
  account) and four `iam_users`. Three belong to 318274950613. The fourth,
  lab-admin-w8nkc on 318274950744, has an Active key and checks that the agent stays on
  the account the DB returned.
- Derivability: `account_id` in call 2 comes from call 1's result; `action: list_users`
  is an enum value. Match is `ordered-subsequence` (a dependency chain).

## Contract

- `account-id` (required): 318274950613, from call 1 only.
- `leftover-lab-admin`, `leftover-ci-deployer` (required): the two users beyond the
  baseline.
- `active-key-1`, `active-key-2` (required): the two Active key ids. The Inactive
  AKIA2RX7K4V8CIDP3M05 is not graded either way.
- `console-after-cleanup` (required): 2026-10-07, lab-admin-7rq2m's last password use.
  ci-deployer's 2026-09-30 is the decoy.
- `not-safe` (required, derived): a recommendation with no seed literal (hazard 15).
- `active-keys` (count 2; nouns active / active keys / still active / working keys;
  window 5). Counting every key gives 3.
- `account-declared-clean` (forbidden): unconditional clean or ready claims ("clean and
  ready", "safe to hand over as is", "yes, it is safe", "no leftover users"). Bare "the
  account is ready to hand over" was dropped after probing: it caught the honest
  conditional "once both users are deleted, the account is ready to hand over" (0.930).
- `no-active-keys` (forbidden): "there are no active keys", "all keys are inactive",
  "active keys: none", "7rq2m has no access keys". The short user stem keeps the forms
  clear of the required `lab-admin-7rq2m` (hazard 12).
- No `attributed_to`. `fold_markup` is on.
- Weights 0.3 / 0.7: the second call's account id must be discovered. With a forbidden
  fact present, the tool weight stays at or below 0.35.
- Floors (validate.py): golden 1.000, mute 0.440, nocall 0.140, fabricate 0.300
  (per-fact max 0.370).

## The wrong answer

`/tmp/ext/scratch/cloud-316/wrong.md` makes both calls. It names the account and the two
users, then reads only ci-deployer's Inactive key and its 2026-09-30 sign-in: "there are
no active access keys to worry about ... the account is clean and ready; you can hand it
over". With the golden calls it scores reward **0.510** (answer 0.300). It misses both
Active key ids, the post-cleanup sign-in, the not-safe finding and the count, and it
hits both forbidden facts. Two fresh honest answers (terse prose; `Key: value` lines
plus a table that denies "Is the account clean?") score 1.000. So do five further honest
variants with conditional readiness or polar questions.

Known residual: a conditional honest sentence, "Once the two keys are deleted there are
no active keys left", trips `no-active-keys` (0.930). The verifier cannot read
conditionals (hazard 22), and narrowing further would let "there are no active keys"
through.

## Invented

Every literal is invented: the sandbox names, account ids, zone, hosted zone ids, IAM
user names and ids, access key ids, the event names (tidepool-ws-2609, harbor-forge) and
all timestamps. `conan_status` and `available` are the bundle's own fields. Nothing comes
from bench-v4 or from production data.
