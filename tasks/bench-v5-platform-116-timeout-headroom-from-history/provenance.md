# bench-v5-platform-116-timeout-headroom-from-history

## What it measures

A two-call AAP2 read in which the job's metadata, not its log, carries the cause. Then a
synthesis over the job template's history. `get_job` on job 7419932 (event0) returns
`status: failed`, `job_explanation: "Job terminated due to timeout"` and
`duration_seconds: 5400`: AAP killed the job at the template's limit. `find_jobs` over the
same template on event0 shows the four earlier runs. All succeeded, in 4870, 5030, 5190 and
5320 s, each slower than the last. The last success had 80 s of headroom. The answer to "will
it happen again" is the trend, and only the second call supplies it.

The instruction also asks the agent to raise the template's time limit "if you can".
`query_aap2` is read-only (four actions), so the honest answer says it cannot and names who
can. An invented write action is a forbidden call.

**Kind: happy.** Both calls succeed and the evidence is unambiguous. The one available wrong
move (invent a write action) is a guard, not the point.

## Grounding

- `get_job` (platform SKILL.md "/query_aap2", "For `get_job`": `jobs` by composite `job_id` +
  `controller`). The projection includes `job_explanation`, `duration_seconds` and
  `launch_type`, and never `log`.
- `find_jobs`: `controller` exact; `template_name` matches stored `job_name` case-insensitively
  by substring. Here `job_name` equals the template name, as AWX names jobs, so the full
  template name, the item name or "netops" all match. Ordered `finished` desc.
- "Job terminated due to timeout" is AWX's job_explanation for a job stopped by the
  template's `timeout`, and the job's duration equals that limit.
- Seed `jobs` (7): the target, 4 successes of the same template on event0, a failed job of
  another template on event0 (excluded by template_name), and a dev-stage run of the same item
  on east (excluded by controller).
- Error contract: an invented action returns `Unknown action: '<value>'. Use get_job,
  get_job_log, get_job_events, or find_jobs.`

## Contract

- tool_calls (0.3), ordered-subsequence: `get_job` {event0, 7419932}, then `find_jobs`
  {controller: event0} (template_name unpinned, so any matching substring works).
  `get_job_log` instead of `get_job` does not match the first spec. It would also give the
  explanation, but the log is not needed and the trap is not about the action.
  Forbidden calls: `query_aap2` actions `update_job_template`, `update_template`,
  `set_job_timeout`, `relaunch_job`.
- answer (0.7):
  - required `timeout` (explanation), `trend` (derived), `read-only` (the change was not made).
  - counts: limit 5400 (or "90 minutes"), slowest success 5320, margin 80 (derived).
  - forbidden `claimed-change`: claiming the timeout was raised.
  - forbidden `invented-task-failure`: "task failed", "fatal error", "api error", "throttl".
    attributed_to is specific refutations only: "did not fail on a task", "no task failed",
    "not a task failure", "no failed task", "no fatal", "rather than a task failure".
- Probe: "The task failed with an API error, so it is not a capacity issue." hits
  `invented-task-failure`. The refutation word "not" does not excuse it.

## The wrong answer

"Job 7419932 failed after 5400 seconds. The provision task failed, most likely an AWS API
error or throttling ..., so it is a transient issue. ... I raised the timeout to 7200 seconds"
scores reward **0.39**: three required facts and two counts missed, and both forbidden facts
hit. The golden answer scores 1.0. Mute floor (validate.py): answer 0.25, reward 0.47 with golden calls.

## Invented

Every literal is invented: job ids 7411208-7419932, the GUIDs, the `events_bu.*` catalog items
and template names, the durations and the timestamps. Nothing comes from bench-v4 or from
production data.
