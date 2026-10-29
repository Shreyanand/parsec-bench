# bench-v5-platform-125-controller-reboot-not-the-playbook

## What it measures

A cross-service correlation in which Icinga *confirms* the mechanism the AAP2 record states.
A teammate blames the `ocp4_workload_amq_streams` role because the log ends in a retry loop.
Two reads settle it:
- `query_aap2 get_job` (or `get_job_log`) on west/6907233: `status: failed`, but
  `job_explanation` is AWX's "Task was marked as running at system start up. The system must
  have not shut down properly, so it has been marked as failed." The controller restarted
  under the job, and no task returned a failure.
- `query_icinga get_downtimes {host: aap2-ctl-west-01.mgmt.example.net}`: a fixed downtime
  by `pnowakowska`, "CHG-58312 kernel patching: rolling reboot of the west controller nodes",
  2026-10-07 22:00-23:00 UTC. The job's `finished` (22:14:31) is inside it. A second downtime
  (CHG-57104, September) is expired and unrelated.

The answer is: planned maintenance killed the job, relaunch it, no code change.

**Kind: trap.** The role-is-broken theory, backed by a log that looks like a hang.

## Grounding

- platform SKILL.md "/query_aap2": `get_job` / `get_job_log` read `jobs` by composite
  `job_id` + `controller`. `job_explanation` is in both projections. The stored log ends in
  `FAILED - RETRYING` lines with no fatal and no recap.
- icinga SKILL.md: `get_downtimes` returns the `downtimes` rows whose `attrs.host_name` equals
  the requested host exactly. The response is `{"result": "<JSON string>"}`, matching the
  bench-v5 icinga tasks' golden results. validate.py WARNs that this serialized string is
  "not in seeds". It is the documented envelope around the seeded rows, so the WARN is
  justified.
- Seed: platform `jobs` 1. icinga `hosts` 1 (the controller, UP), `downtimes` 2.
- leakage.py: clean. The earlier `re-run` weak-literal WARN was removed by dropping that form.

## Contract

- tool_calls (0.3), unordered-subset: `query_aap2` {controller: west, job_id: 6907233}
  (action unpinned: get_job or get_job_log) and `query_icinga` {get_downtimes, host}.
- answer (0.7): required `explanation`, `change` (CHG-58312), `author`, `inside-window`
  (derived), `relaunch` (derived). Forbidden `role-blamed` ("role is broken", "bug in the
  role", "kafka cluster never became ready", ...), excused only by specific attributions or
  refutations ("teammate's theory", "teammate thinks", "teammate suspects",
  "role did not fail", "role didn't fail", "not the role", "is not the cause",
  "never got a failed result"). Forbidden `old-downtime` (blaming the expired CHG-57104).
- Probe: "The role is broken, not the controller." hits `role-blamed` (reward 0.40).

## The wrong answer

"Job 6907233 failed in the ocp4_workload_amq_streams role: the Kafka cluster never became
ready ... Your teammate is right that the role needs fixing" scores reward **0.40**: all five
required facts missed, and the forbidden fact hit. The golden answer scores 1.0. Mute floor
(validate.py): answer 0.29, reward 0.50 with golden calls.

## Invented

Every literal is invented: job 6907233, GUID v3pkd, the controller host and address, the
change numbers, the authors, the times and the `integration_bu.event-streaming-lab` item. The
job_explanation sentence is AWX's real wording for this case. Nothing comes from bench-v4 or
from production data.
