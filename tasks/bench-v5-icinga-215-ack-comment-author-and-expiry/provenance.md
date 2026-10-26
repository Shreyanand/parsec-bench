# bench-v5-icinga-215-ack-comment-author-and-expiry

**Kind:** happy. **Services:** icinga. **Calls:** 1. **Weights:** 0.2 / 0.8.

## What it measures

Reading an acknowledgement out of Icinga's comment objects: which comment *is* the
acknowledgement (`entry_type` 4), who set it, its reason, and when it lapses
(`expire_time`). `get_comments` on `ptp-grandmaster-osl-2` returns three comments:

- the acknowledgement on `ptp-phase-err` by `ichikawa.r` (2026-11-24 09:40 UTC; GNSS antenna
  feed weak after roof work, Meinberg case SR-77140), `expire_time` 2026-11-27 18:00 UTC;
- a later ordinary user comment (`entry_type` 1) on the same service by `pmbeki`
  (2026-11-24 13:15 UTC: phase error jumped to 4.1 us, held flat, watching only);
- a host-level user comment by `vdalgaard` about a rack B4 PDU swap.

The agent must attribute the acknowledgement to the `entry_type` 4 author rather than the most
recent commenter, convert the `expire_time` epoch, and say that the acknowledgement expires by
itself rather than being held until removed.

## Grounding

- `get_comments` reads only `comments`, filters by exact `attrs.host_name` (host-level and
  service rows both), ignores `search`/`filter_expr`, and returns rows verbatim (SKILL.md
  "Store reads", "Filtering rules"). A call with `service: ptp-phase-err` as well returns the
  two service comments, which carry every graded fact.
- `entry_type` (Icinga2 CommentType: 1 User, 4 Acknowledgement), `expire_time` and
  `persistent` are Icinga2 Comment attributes stored in the free-form `attrs`; the bundle's own
  db.json carries `entry_type` and `persistent` on comments.
- The `services` row is consistent: `acknowledgement` 1 and `acknowledgement_expiry` equal to
  the comment's `expire_time`, so an agent that also reads `get_services` sees no contradiction.

## Contract

- Expected call: `get_comments` with `host: ptp-grandmaster-osl-2`.
- Required: `acker` (ichikawa.r); `ack-reason` (SR-77140 / GNSS / antenna / roof work);
  `expiry-date` and `expiry-time` (derived from the epoch 1795802400, with notes);
  `other-note` (the content of pmbeki's note: 4.1 us, held flat, watching only). The other
  note is graded by content, not by pmbeki's name, so it does not entangle with the forbidden
  `wrong-acker` forms.
- Forbidden: `wrong-acker` ("acknowledged by pmbeki", "pmbeki acknowledged", ...) and
  `no-expiry` ("never expires", "held indefinitely", "until someone removes it", ...). No
  `attributed_to`. Polarity checked: "The alert was not acknowledged by pmbeki" and "Does the
  acknowledgement have no expiry? No" are not hits.
- Mute floor 0.429 (2 forbidden of 7 items), nocall 0.229, fabricate 0.200 (max per-fact
  0.314, below mute).

## The wrong answer

"The alert was acknowledged by pmbeki at 13:15 UTC ... The acknowledgement is held indefinitely
until someone removes it." (`/tmp/ext/scratch/bench-v5-icinga-215-ack-comment-author-and-expiry/wrong.md`).
Reward 0.543: answer 0.429. It hits both forbidden facts and misses the expiry date and time.

Two fresh honest answers (terse prose; and `Key: value` lines that explicitly deny pmbeki
acknowledged it) both score 1.000.

## Invented

The host, services, people, case number, comment texts, addresses and epochs are invented for
this task. Nothing comes from bench-v4 or from production data.
