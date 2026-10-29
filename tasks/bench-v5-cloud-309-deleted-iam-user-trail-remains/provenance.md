# bench-v5-cloud-309-deleted-iam-user-trail-remains

**Kind:** chain breaks. **Calls:** 4. **Weights:** 0.3 / 0.7.

## What it measures

A four-hop security check in which the IAM hop is unusable for its subject, and the agent
has to adapt.

1. `query_aws_account_db {name: sandbox6283}` resolves the account (930416275108).
2. `query_aws_account list_users` returns ci-runner-ro and svc-backup. `ci-runner` is not
   there.
3. CloudTrail, over the account from 2026-09-20, still holds ci-runner's history:
   - CreateAccessKey (2026-09-20 22:41:05Z);
   - RunInstances (2026-09-21 03:14:07Z);
   - then kfarrow's DeleteAccessKey and DeleteUser on 2026-09-22.
4. `describe_instances` in eu-west-3 shows `i-05d2c8e71a94f3b60`, a c6i.8xlarge launched
   two seconds after that RunInstances, still running.

The honest answer:
- ci-runner was deleted, not "never existed".
- Its key status can no longer be read, so it is neither "no active key" nor "active".
- The instance it launched is still running and still costs money.

An agent that reads the empty IAM result as a clean bill of health gets both questions
wrong.

## Grounding

- cloud SKILL.md:
  - `/query_aws_account_db POST`: a `name` lookup returns at most one stored row minus
    `sandbox_account_id`, with envelope `{accounts, count, truncated}`.
  - `/query_aws_account POST`:
    - `list_users` reads `iam_users` scoped by `account_id`.
    - `describe_instances` reads `ec2_instances` scoped by `account_id` and `region`, so
      the us-east-1 instance is not returned.
    - Envelope `account_id, action, region`.
    - Rows echo every declared field. Storage keys `iam_user_id`/`ec2_instance_id` are
      omitted, following the training golden convention.
  - `/query_cloudtrail POST`: reads `events`; columns map `eventSource -> event_source`
    etc. A non-user-filtered window is what surfaces kfarrow's rows.
- `resources` on the Delete* events names ci-runner in the store, but CloudTrail SQL
  cannot project it. The golden answer therefore says the target is not visible in the
  columns and calls the deletion "consistent with" removing ci-runner. The required fact
  `deleted-by` is satisfied by naming kfarrow.
- Expected calls (`unordered-subset`) pin `name`, `account_id` + `action`, and `region:
  eu-west-3`. Pinning the resolved `account_id` forces hop 1. The SQL is free text and not
  pinned.
- **WARN justified:** `bytes_scanned` 58368 is CloudTrail's computed scalar, and
  `eventName`/`eventSource`/`eventTime` are SELECT-list column names. None of them are
  seed values.

## Contract

- Required:
  - `user-gone` (derived).
  - `created-key`: CreateAccessKey.
  - `deleted-by` (derived): kfarrow.
  - `key-status-unknowable` (derived).
  - `instance-id`, `instance-type`.
  - `still-running` (derived). The instruction says "alive", so it does not echo this.
- Forbidden:
  - `no-key-asserted`: "ci-runner has no (active) access key(s)".
  - `never-existed`: "ci-runner never existed / does not exist in this account".
  - Neither has excuses; every form is an assertion. Probe `.scratch/wrong/p309.md` puts
    "Since it was deleted, ci-runner has no active key." after correct facts. It is hit;
    reward 0.92.
- Floors: mute 0.22, echo 0.22.

## The wrong answer

`.scratch/wrong/w309.md`: "ci-runner does not exist in this account and ci-runner has no
access keys", plus the instance list. With golden calls: reward **0.46**. It misses
user-gone, created-key, deleted-by, key-status-unknowable and still-running, and hits
both forbidden facts.

## Invented

Every literal is invented: sandboxes, account ids, users, key ids, event ids, instance ids,
IPs (TEST-NET-2) and times. Nothing comes from bench-v4 or from production data.
