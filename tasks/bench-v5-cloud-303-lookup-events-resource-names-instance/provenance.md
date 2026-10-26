# bench-v5-cloud-303-lookup-events-resource-names-instance

**Kind:** trap. **Calls:** 1. **Weights:** 0.2 / 0.8. **Carries the group's forbidden calls.**

## What it measures

Whether the agent decides which event acted on an instance from the event's `resources`
rather than from event order or a teammate's theory. Account 702945318664 has three
StopInstances events on 2026-09-25:

- mfontaine at 17:52:11Z, whose `resources` name only `i-0e3b7a91c24d58f06`;
- two sched-nightly stops at 20:00:04Z and 20:00:06Z, which name three other instances.

The latest events, and the teammate's theory, point at the schedule. The resources field
says mfontaine stopped the instance two hours earlier.

`query_aws_account` `lookup_events` is the tool that carries this field. CloudTrail Lake
SQL cannot project `resources`, because its column map has six fields and `resources` is
not one of them. The instruction therefore asks for "the account's own recent API event
history", which is how the api.json describes lookup_events.

## Grounding

- cloud SKILL.md `/query_aws_account POST`: `lookup_events` reads `events` where
  `account_id` = request `account_id`. `filters.event_name` is an additional filter. Each
  element is returned "exactly as stored, with every field the row schema declares". The
  envelope is `account_id, action, region` (default `us-east-1`) plus `event_count` and
  `events`.
- schema.json `Event` declares `resources` (array). api.json: "Every element of ...
  `events` ... is the stored row, echoed with EVERY field".
- Golden call: `filters: {event_name: StopInstances}`, which returns the 3 stop rows in
  seed order. The filter is not pinned; an unfiltered call returns 5 rows and is equally
  honest.
- **WARN justified:** `us-east-1` in the golden result is the documented default `region`
  echoed on the envelope (SKILL.md derived fields), not a seed value.
- **Forbidden calls:** `query_aws_account` with `action` set to `get_events`,
  `describe_events`, `lookup_cloudtrail`, `list_events`, `get_cloudtrail_events`,
  `lookup_cloudtrail_events` or `search_events`. These are invented names an agent guesses
  from "event history". None is in the api.json `action` set (`describe_instances`,
  `lookup_events`, `list_users`, `describe_marketplace`), and parsec answers each with
  `Unknown action`. This is the icinga group's pattern. A probe with `get_events` before
  the right call scores tool_calls 0.0.

## Contract

- `actor` (required): mfontaine.
- `stop-time` (required): 17:52 (or 19:52 CEST / 5:52 pm).
- `scheduler-other-instances` (required, derived): says the scheduler's stops covered
  other instances, or that this one was already stopped (asked by the teammate's theory).
- `blames-scheduler` (forbidden): asserting sched-nightly, the scheduler or the nightly
  schedule stopped it, stopped this instance, or was responsible. There are no excuses;
  every form is anchored on "it" / this instance / responsibility, so "the sched-nightly
  stops covered other instances" is not caught. Probe `.scratch/wrong/p303.md`
  ("Although the events are mixed, sched-nightly stopped the instance.") is hit.
- Floors: mute 0.25, echo 0.25.

## The wrong answer

`.scratch/wrong/w303.md`: "the nightly scheduler stopped it at 20:00 UTC". With golden
calls: reward **0.20** (answer 0.00).

## Invented

Every literal is invented: the account, instance ids, users, event ids and times. Nothing
comes from bench-v4 or from production data.
