# bench-v5-platform-146-assumed-role-session-outlived

## What it measures

A three-hop RCA (log, catalog item, agnosticv config) on a failure class no existing
task has: **temporary credentials that expire mid-run**. The job assumes the sandbox
role once, at 14:06:53, and the catalog item's `common.yaml` sets
`sandbox_aws_session_duration: 3600`. The cluster install takes about 41 minutes and
the workload phase runs on, so the last AWS call (`PutBucketPolicy` at 15:06:58) lands
60 minutes after the session started and AWS refuses it with `ExpiredToken`.

The instruction voices the obvious reading: the security team's access-key rotation ran
at 14:30, so it must have revoked the keys, and the remedy is to re-issue them. The log
refutes that twice: the same session created the S3 bucket at 14:54:11, after the
rotation, and the error code is `ExpiredToken`, not the error of a revoked key. Only the
catalog item says how long the session lives, so the agent must join the config's
lifetime with the log's own timestamps.

## Tranche

**Challenge.** Expected to score below 1.0 for a good agent. The agent failure it
exposes is **taking a credential error as a credential problem**: "security token"
plus a rotation in the same afternoon is a ready-made story with a ready-made remedy.
The refutation needs a timeline read of the log (an AWS call that succeeded after
14:30) and the cause needs a value only the catalog item carries, compared against a
difference of two timestamps no string states.

## Grounding

- `query_aap2 get_job_log`: composite `job_id` + `controller` on `jobs` (platform
  SKILL.md "Store reads"); the golden result is the documented `get_job` projection plus
  `log*`. Controller `partner0` is an api.json enum value.
- `lookup_catalog_item` (github SKILL.md): the search is lowercased and `_` becomes `-`;
  the stored row's lookup key is its `directory` `telemetry-datamart-lab`, so the bare
  name and the Babylon form `datalake_bu.telemetry-datamart-lab.prod` from the job name
  both hit. It returns `path` `datalake_bu/telemetry-datamart-lab` and `files` `common.yaml`, `prod.yaml`.
- `fetch_github_file`: exact `(owner, repo, path, effective ref)`; the item's two files
  are seeded under `HEAD` and `main` (the default branch). The expected path is
  `path + "/" + files[0]` of the lookup result (the gate's one-dict join). `prod.yaml`
  is seeded so an agent that reads it gets content (it carries no credential setting).
- The job carries `git_revision`, but no expected call reads the job's own repository
  (agnosticd), so nothing is seeded under that revision.

## Contract

Weights 0.3 / 0.7, `ordered-subsequence` (a strict chain: the lookup needs the item
name from the log, the fetch needs the lookup's path).

- `expired-token`: the AWS error. Earned by any reader of the log.
- `session-setting`: `sandbox_aws_session_duration`, only in common.yaml.
- `session-seconds`: `3600`, only in common.yaml.
- `outlived` (derived): the run is longer than the session.
- `rotation-not-cause` (derived): the decoy refuted.
- count `minutes-after-assume` = 60 (window 4), with "one hour" phrasings in
  `extra_any_of`.
- forbidden `rotation-revoked` and `clock-skew`, written as claims (hazard 22); `rotation-revoked` carries `attributed_to` only for
  sentences that name the user's theory to reject it ("the assumption that the rotation
  revoked the keys"); a plain denial ("not caused by the rotation") is excused by the
  polarity-aware verifier.

Mute answer floor: 2 forbidden of 8 answer items, reward 0.475.

## The wrong answer

`/tmp/ext/scratch/bench-v5-platform-146-assumed-role-session-outlived/wrong.md`: reads the log, sees "security token", blames the
14:30 rotation and recommends re-issuing the keys. With the golden calls it scores **0.475**
(answer 0.25: it earns `expired-token` and the clock-skew forbidden fact only); a second
phrasing (`wrong2.md`) also scores 0.475. Golden 1.000.

Honest panel, all **1.000**: three authored answers (`honest1-3.md`: terse prose, a table
with `Key: value` lines denying the rotation, and a refute-by-restating answer) and three
blind answers written by a separate agent from the instruction and the tool results only
(`blind-a/b/c.md`). Two blind answers first scored 0.9125 ("had simply run out"; a
counterfactual "If the rotation had revoked the credentials, ..."), so `outlived` was
widened and the conditional was added to `attributed_to`. Residual: an answer that blames
the rotation but quotes `ExpiredToken` earns that one fact (bar C).

## Invented

Every literal is invented: job 7731456, GUID `q8zvw`, the catalog item
`datalake_bu/telemetry-datamart-lab`, the role names `sandbox_aws_session` and
`ocp4_workload_datamart`, the variable `sandbox_aws_session_duration`, the IAM role
`rhdp-sandbox-provisioner`, account 613027954418, bucket `rhdp-q8zvw-warehouse`, the
revision and every timestamp and figure. The incident class (an assumed-role session
shorter than the job that uses it) is invented in the mould of bench-v4's challenge
tranche; no public postmortem is its source, and nothing comes from bench-v4 or
production data.
