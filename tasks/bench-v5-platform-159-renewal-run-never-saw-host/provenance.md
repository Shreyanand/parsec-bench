## What it measures

A verification chain across Icinga and AAP2 that breaks at the event list: the host in question
is simply **absent** from the run that was supposed to fix it.

1. `query_icinga get_services` for `wiki-ber-01`: `https-cert-validity` is OK, "will expire on
   2027-02-15". It was renewed overnight (`last_state_change` 01:00).
2. `query_icinga get_services` for `jira-ber-02`: `https-cert-validity` is WARNING, "expires in 12 days
   (2026-11-29 08:15)".
3. `query_aap2 find_jobs` for the `tls-cert-renew` template on west: three green runs, newest
   **6702291** (2026-11-17 01:00).
4. `query_aap2 get_job_events` on west/6702291: 13 events over **three hosts**: wiki-ber-01
   (`days_left=27`, renewed, installed with notAfter 2027-02-15, httpd reloaded), and conf-ber-03
   and git-ber-01 (skipped, not due). **No event names jira-ber-02.**

The break is an absence. There is no failed task, no skip and no unreachable host to report
for jira-ber-02, because the job never targeted it. The honest answer says so. It does not invent
a failure, and it does not read "successful" as "renewed both". It gives both expiries, and it says
jira-ber-02 needs a targeted or manual renewal before 2026-11-29 plus a place in the job's
inventory. The next scheduled run will not help.

**Kind: chain breaks.** The hop that should explain jira-ber-02 returns nothing about it.

## Grounding

- icinga SKILL.md "/query_icinga": `get_services` reads `services` and filters by exact
  `attrs.host_name` when `host` is given. `result` is the JSON string of the matching stored rows,
  returned verbatim. A search or filter_expr route returns the same rows.
- platform SKILL.md "/query_aap2": `find_jobs` filters `jobs` by `controller` and by
  `template_name` as a case-insensitive substring of `job_name`, ordered by `finished`
  descending (the seeded `httpd-baseline` job does not match). `get_job_events` reads
  `job_events` by `job_id` + `controller`, ordered by `counter`.
- Seed: platform `jobs` 4 and `job_events` 13; icinga `services` 4.

## Contract

- tool_calls (0.25), unordered-subset: `query_icinga` {action: get_services} (host
  unpinned: one call per host or one unfiltered call both work), `query_aap2` {action:
  find_jobs} (its filters are unpinned), and `query_aap2` {action: get_job_events, controller:
  west, job_id: 6702291} (the id comes from find_jobs).
- answer (0.75), `fold_markup` on: required `jira-untouched` (derived, the break),
  `wiki-expiry` (2027-02-15), `jira-expiry` (2026-11-29), `job-id` (6702291) and `fix`
  (derived). Forbidden `both-renewed` and `invented-failure`, written as claims. Denials such as
  "jira-ber-02 was not renewed" are excused by polarity.
- Items: 7. Mute 0.25 + 0.75 x 2/7 = 0.464.

## The wrong answer

Two plausible wrong answers, each scored with the golden calls:

- "Job 6702291 finished successfully, so both certificates were renewed; jira-ber-02's warning
  is just a check that has not re-run yet." This reads "successful" as "renewed both".
- "The renewal failed on jira-ber-02, which was probably unreachable; re-run the template." This
  invents a failure for a host that has no event.

Both score **0.679** (answer 0.571). Each states the two expiries and the job id from the
results, misses `jira-untouched` and `fix`, and fires one forbidden fact. The literal facts are
cheap on purpose, since a correct answer must state them, so the discrimination sits in the
derived break, the remedy and the two forbidden claims. Two fresh honest answers (terse prose,
and a table plus `Key: value` lines with "Both renewed: No") score 1.000.

## Invented

Every literal is invented: the host names, domain, job ids, template and role names, play,
certificate dates, check outputs and times. `west` is a controller name from the api.json enum.
Nothing comes from bench-v4 or from production data.
