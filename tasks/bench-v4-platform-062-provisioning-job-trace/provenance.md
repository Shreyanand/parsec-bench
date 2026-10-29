# bench-v4-platform-062-provisioning-job-trace

Idea from bench-h4_Oct5 062 (external, 2026-10-05); re-authored; every value derived from this seed.
It also absorbs the idea of bench-h4_Oct5 035 (find a job by GUID with no controller, then take
the cause from the job's events rather than the job record), merged here by owner decision
2026-10-07.

**Kind:** trap. A same-template failed job for a different GUID, on another controller, sorts
first in any search that does not filter by this account's GUID; reading it yields no graded
literal. Stopping at the job record yields no cause.

## What it measures

A three-hop, two-service chain in which every identifier after the first is discovered:

1. `query_aws_account_db {name: sandbox4718}` (cloud). parsec's `sandbox_accounts` row carries a
   `guid` but no job id or controller. Bundle: `harness-skills/parsec-cloud/SKILL.md`
   `/query_aws_account_db`, "When `name` is provided -- read `sandbox_accounts` by `name`, return
   at most one row".
2. `query_aap2 {action: find_jobs, template_name: wq4ke}` (platform) with **no controller**.
   parsec's `_find_jobs` (`vendor/parsec/src/tools/aap2.py:331-384`) queries every configured
   controller in parallel when `controller` is empty, and `template_name` becomes
   `name__icontains` on the job *name* (`aap2.py:323`). Bundle: `parsec-platform/SKILL.md`
   `/query_aap2` "For `find_jobs`" (case-insensitive substring on the job name; `controller`
   filter only when supplied) and the error section ("Do NOT return this error if `controller`
   is omitted for `find_jobs`"). The result is `JobSummary` rows only (nine fields, no
   `job_explanation`, no task).
3. `query_aap2 {action: get_job_events, controller: event0, job_id: 66215}`. The failing task
   and its error exist only in `job_events` (`_get_job_events`, `aap2.py:260-303`). The job row's
   `job_explanation` is `""`, as AAP leaves it for a playbook task failure, so `get_job` does
   not give the cause either.

## Seed design

cloud `sandbox_accounts` (all other cloud collections `[]`):

| name | guid | role |
|---|---|---|
| sandbox4718 | wq4ke | **target** account |
| sandbox4719 | fn8tj | the decoy job's account (never returned by the name lookup) |

Both comments are the uninformative `provision failed - AAP2 job not linked`; no cause word is
in the cloud seed. No nulls: `reservation` is `""`, `annotations` is `{}`.

platform `jobs` (template `RHPDS agd-v2.rhel-edge-fleet.prod-provision` for the first two):

| job_id | controller | guid in job_name | status | finished | role |
|---|---|---|---|---|---|
| 66231 | west | fn8tj | failed | 2026-06-03T14:02:18Z | **decoy**, same template, sorts first |
| 66215 | event0 | wq4ke | failed | 2026-06-02T09:21:37Z | **target** |
| 66198 | east | pd2rm | successful | 2026-06-01T07:31:52Z | unrelated item |

Job names follow the `<item>-<guid>-<n>-provision` shape `_extract_guid`'s regex expects
(`aap2.py:62`). Only 66215's name contains `wq4ke`, so the golden `find_jobs` returns exactly one
row. A search on the template / env type (`rhel-edge-fleet`) instead returns 66231 first.

platform `job_events`: 66215 has three (counter 41 VPC ok, 42 subnet ok, 43
`runner_on_failed` "Allocate the bastion Elastic IP", role `infra_aws_bastion`, error
`AddressLimitExceeded` from `AllocateAddress`). 66231 has two (a fleet-manager route-admission
timeout). Every event row carries all fourteen schema fields including `job_event_id`,
`event_key`, `controller` and `job_id` (CLAUDE.md item 2). All other platform collections are
`[]`, including `workshops` and `babylon_workshops`. No job carries a `log`, so the cause is not
reachable through `get_job_log` either.

`event0` is one of the bundle's four enum-constrained controller names (`east`, `west`,
`event0`, `partner0`); it is shared with batch 035's seed only because the schema forces the
choice. No other value, id, name or sentence was taken from either batch scenario.

## Golden results

Full stored rows, omitting the synthetic storage keys `sandbox_account_id` and `job_event_id`
(the convention of `bench-v4-cloud-024` and `bench-v4-platform-004`); envelopes narrowed to the
keys the SKILL.md sections guarantee (`accounts`/`count`; `total`/`jobs`;
`job_id`/`controller`/`event_count`/`events`), since `bench.replay` allows extra live keys but
not missing ones. `find_jobs` rows are the nine `JobSummary` fields.

## Contract

Expected calls (ordered-subsequence), pinning identifiers only:

- `query_aws_account_db {name}` -- the account name, stated in the instruction.
- `query_aap2 {action: find_jobs, template_name: wq4ke}`. **`template_name` is pinned, and that is
  a deliberate decision.** The GUID is the identifier this hop exists to carry, and
  `template_name` is the only `find_jobs` argument that can carry it (`aap2.py:323`); a
  `find_jobs` without it is an unfiltered listing, not the correlation step. The value is the
  bare GUID, the one natural spelling, taken verbatim from call 1's result. `controller` is
  neither pinned nor declared in `absent_args`: an agent that loops over the four controllers
  with the GUID filter has made a legitimate search, and penalising it would grade style. An
  agent that passes a decorated value (`-wq4ke-`) loses this call; recorded as a live-replay
  concern rather than widened, since the verifier cannot express substring-of-argument.
- `query_aap2 {action: get_job_events, controller: event0, job_id: 66215}` -- both from call 2's
  result. `failed_only` is not pinned.

Required facts (no forbidden facts): `job-id` (66215), `controller` (event0), `failing-task`
(the bastion Elastic IP allocation), `cause` (AddressLimitExceeded / Elastic IP limit). No form
occurs in `instruction.md` or in the decoy's job or event rows.

## Weighting

`0.3 / 0.7`. The chain is genuinely dependent (each hop's identifier comes from the previous
result), but the discriminating content is the cause, which only the third hop reaches. No
forbidden answer fact is declared: the wrong readings are the decoy job and an invented cause,
and every decoy literal is in the seed (hazard 14), while an invented cause is unbounded in
phrasing (hazard 8), so no finite high-precision forbidden list exists. Gate floors: mute 0.300,
nocall 0.000, fabricate n/a.

## Measured residual (acceptance bar C)

`job-id` and `controller` are asked for and are earned at the `find_jobs` hop, so an agent that
stops there and invents a cause scores 0.650 with the golden calls held (0.550 with its real
two-call trajectory), above the 0.300 mute floor. It states two true graded literals; the cause
facts it cannot earn. This is partial credit, not a defect: the instruction asks for the job id
and controller, and a forbidden fact that could catch an arbitrary invented cause does not exist.
A decoy reading (66231 / west / route timeout) scores at the mute floor.
