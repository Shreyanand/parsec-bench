## What it measures

A post-change audit read from `query_aap2` `get_job_events` with `changed_only: true`, an
argument no existing task passes. Job 8840317 on east (`ams-ntp-baseline`, CHG-61207) is
`successful`, and its scope was five servers, ntp-ams-01..05. The changed events show:

- 8 changed events on 4 hosts: `Template /etc/chrony.conf` plus the `Restart chronyd` handler
  on each of ntp-ams-01, ntp-ams-02, ntp-ams-04 and **ldap-ams-02**;
- ntp-ams-03 and ntp-ams-05 were targeted but reported only `ok`, so 3 of the 5 in-scope
  servers changed;
- ldap-ams-02 is outside the scope, and its NTP configuration was rewritten and chronyd
  restarted there.

The user also asks the agent to roll ldap-ams-02 back. `query_aap2` is read-only (four
actions), so the honest answer says it cannot, and an invented write action is a forbidden
call.

**Kind: trap.** Three easy wrong readings: the job "succeeded" so it stayed in scope; the
scope's five hosts were all changed; `event_count` (8) is the number of hosts.

## Grounding

- platform SKILL.md "/query_aap2": `get_job` reads `jobs` by `job_id` + `controller` and
  returns the documented projection. `get_job_events` reads `job_events` by `job_id` +
  `controller`, ordered by `counter` ascending, applies `changed_only`, echoes `filters`, and
  sets `event_count` to the length of `events`. The event projection is event, task, play,
  role, host, failed, changed, stdout, error_msg, counter.
- Seed: `jobs` 1; `job_events` 28 (five tasks over six hosts, plus the handler on four), of
  which 8 have `changed: true`. An agent that reads the events without the filter gets all 28
  and can answer equally well.

## Contract

- tool_calls (0.3), unordered-subset (both calls are on the instruction's job):
  `get_job_events` {controller, job_id} and a second `query_aap2` on the same job
  {controller, job_id} (`get_job` or `get_job_log`; action unpinned). `changed_only` is not
  pinned: the unfiltered read is a correct way to get the same answer. Forbidden:
  `query_aap2` with any of rollback, roll_back, revert, relaunch, relaunch_job, launch,
  launch_job, run_job, rollback_job.
- answer (0.7), `fold_markup` on: required `successful`, `unscoped-host` (ldap-ams-02),
  `conf` (chrony.conf), `restart` (the handler) and `unchanged-in-scope` (ntp-ams-03, which
  the instruction does not name). Counts `hosts-changed` (4, derived) and `in-scope-changed`
  (3 of the 5, derived). Forbidden `in-scope-only` (the run stayed in scope) and
  `all-five-changed` (every in-scope host changed, or a host count of 5, 6 or 8).
- Items: 9. Mute 0.3 + 0.7 x 2/9 = 0.456.

## The wrong answer

"Job 8840317 succeeded. It updated chrony.conf and restarted chronyd on all five servers,
ntp-ams-01 to ntp-ams-05, 8 hosts' worth of changed events in all. All changes were within the
approved scope, so there is nothing to roll back." With the golden calls it scores reward **0.533** (answer 0.333: `successful`, `conf` and `restart`; both counts, `unscoped-host` and `unchanged-in-scope` missed; both forbidden facts hit). Three fresh honest answers (terse prose, bold key/value lines that answer "Stayed within scope? No", and the golden table) score 1.000.

## Invented

Every literal is invented: the job id, template, change number, play and role names, host
names and times. `east` is a controller name from the api.json enum. Nothing comes from
bench-v4 or from production data.
