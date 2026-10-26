# bench-v5-cloud-314-deleterule-two-event-sources

**Kind:** trap. **Calls:** 1. **Weights:** 0.2 / 0.8.

## What it measures

Whether the agent separates CloudTrail events that share an `eventName` but come from
different services, using `eventSource`. `DeleteRule` is the API name of two unrelated
deletions: an ALB listener rule (`elasticloadbalancing.amazonaws.com`) and an EventBridge
rule (`events.amazonaws.com`). The user asks who deleted the load balancer's listener
rules in account 274619035821 between 13:00 and 15:00 UTC on 2026-09-17, how many, the
first and last times, and the event source.

In that window the store holds five `DeleteRule` events:
- three from `elasticloadbalancing.amazonaws.com` by hvesterlund (13:24:51Z, 13:58:06Z,
  14:38:12Z), each naming a `listener-rule` ARN on `storefront-public-alb`;
- two from `events.amazonaws.com` by pdasgupta (13:09:44Z, 14:52:18Z), naming EventBridge
  rules.

A query on `eventName = 'DeleteRule'` alone returns all five. An agent that does not read
or filter on `eventSource` reports 5 listener rules, two actors, and the decoy's times as
the first and last. A window decoy sits just outside: jokafor's ELB `DeleteRule` at
15:12:40Z.

## Grounding

- cloud SKILL.md `/query_cloudtrail POST`:
  - Store access: "Read only `events`"; column map `eventTime -> event_time`,
    `eventName -> event_name`, `eventSource -> event_source`,
    `recipientAccountId -> account_id`, `userIdentity.username -> username`.
  - Aliased items are named by their alias; success body
    `{columns, rows, row_count, bytes_scanned, truncated}`.
- api.json SIMULATION STORE AUTHORITY paragraph: every WHERE predicate is evaluated on the
  mapped stored field, and "Timestamp comparisons compare instants".
- The SQL is free text and is not pinned (expected call `query_cloudtrail` with `{}`).
  Filtering on `eventSource` directly, or selecting it and filtering client-side, are
  both correct routes.
- Seed `events` (all account 274619035821, 2026-09-17): the five in-window `DeleteRule`
  rows above, plus hvesterlund's `ModifyRule` (12:41:15Z) and `DescribeRules`
  (13:18:02Z), and jokafor's ELB `DeleteRule` at 15:12:40Z.
- Golden result: the five in-window `DeleteRule` rows in time order, with columns
  `eventTime, eventName, eventSource, username`. `bytes_scanned` 47104 is the one computed
  scalar (SKILL.md: deterministic and positive when rows match).
- Both `DeleteRule` sources are real: ELBv2 `DeleteRule` deletes a listener rule, and
  EventBridge `DeleteRule` deletes an event rule.

## Contract

- `actor` (required): hvesterlund.
- `first-deletion` / `last-deletion` (required): 13:24:51 and 14:38:12. Reading every
  `DeleteRule` gives 13:09:44 and 14:52:18 instead.
- `event-source` (required): `elasticloadbalancing.amazonaws.com` (or "Elastic Load
  Balancing", "ELBv2"). The instruction says "load balancer", which none of the forms
  contains.
- `listener-rule-deletions` (count 3; nouns listener rules / rules / deletions /
  DeleteRule / events / calls; window 5). Wrong scopes give 5 (all `DeleteRule` in the
  window), 4 (ELB only, window ignored) and 6 (whole afternoon).
- `eventbridge-actor-blamed` (forbidden): claims tying pdasgupta to listener or
  load-balancer rules. "pdasgupta deleted" alone is true (of EventBridge rules), so it is
  not forbidden (hazard 14). No `attributed_to`; denials are read by polarity.
- `listener-rule-count-inflated` (forbidden): "5 listener rules", "4 listener rules"
  and ALB / load-balancer variants. "5 DeleteRule events" is true and is not forbidden.
- `fold_markup` is on, so `` `hvesterlund` `` and `**3**` read plainly.
- Weights 0.2 / 0.8: one call on an account the instruction gives; the answer carries
  the discrimination.
- Floors (validate.py): golden 1.000, mute 0.429, nocall 0.229, fabricate 0.200
  (per-fact max 0.314).

## The wrong answer

`/tmp/ext/scratch/cloud-314/wrong.md`: queries `DeleteRule` in the window without
reading `eventSource` and reports "Five listener rules were deleted ... hvesterlund
deleted three and pdasgupta deleted two of the listener rules", first 13:09:44, last
14:52:18. With the golden calls it scores reward **0.314** (answer 0.143). It misses the
two times, the event source and the count, and hits both forbidden facts. Two fresh
honest answers (terse prose; `Key: value` lines plus a table that denies the
pdasgupta reading) score 1.000.

Known residual: "Two of the listener rules were deleted by pdasgupta" evades
`eventbridge-actor-blamed`, because "were deleted by pdasgupta" is true of the
EventBridge rules and cannot be forbidden. Such an answer still misses the count, the
times and usually the event source.

## Invented

Every literal is invented: the account id, usernames, event ids, rule ARNs, the load
balancer name and the times. `elasticloadbalancing.amazonaws.com` and
`events.amazonaws.com` are real AWS service endpoints. Nothing comes from bench-v4 or
from production data.
