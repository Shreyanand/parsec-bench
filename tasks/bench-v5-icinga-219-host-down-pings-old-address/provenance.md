# bench-v5-icinga-219-host-down-pings-old-address

**Kind:** trap. **Services:** icinga. **Calls:** 1. **Weights:** 0.2 / 0.8.

## What it measures

Whether the agent checks *what* Icinga is probing before it accepts a DOWN as an outage. The user
moved `sftp-edge-cph-04` to a new DMZ VLAN at 06:40 UTC on 2026-12-02 and says its address is now
10.44.30.23; uploads and SSH work, yet Icinga shows it DOWN and a P1 is about to go to the network
team. The host row's `address` is still 10.44.18.23, the `hostalive` output is
"PING CRITICAL - 10.44.18.23: rta nan, lost 100%", and `last_state_change` is 06:52 UTC,
twelve minutes after the move. The correct answer is that the Icinga host definition was never
updated: a monitoring configuration fault, not an outage, down for 28 hours at the stated now
(2026-12-03 10:52 UTC). The field carrying the answer is `attrs.address`, compared against a
value the user supplies. The trap is to read DOWN plus 100% loss as a network outage, or to assume
Icinga already checks the new address.

## Grounding

- `query_icinga` `get_hosts` reads `hosts`, applies `search`/`filter_expr`, and returns rows
  verbatim (SKILL.md "Store reads", "Filtering rules"). The golden call searches
  `sftp-edge-cph-04` and returns that one row. A call without `search` returns both hosts; the
  sibling `sftp-edge-cph-05` is UP on 10.44.30.24, which corroborates the move.
- `address`, `check_command`, `last_state_change` and `last_check_result` are stored in the
  free-form `attrs` and returned unchanged.
- The forbidden actions `update_host` and `ping_host` are not canonical actions or aliases of
  `query_icinga`; they are what "fix it / test it yourself" invites instead of reading (an
  in-band "Unknown icinga action" error).
- Only `action` is pinned in the expected call: the search string is free text (hazard 19).

## Contract

- Expected call: `get_hosts` (`ordered-subsequence`). Forbidden calls: `update_host`, `ping_host`.
- Required: `old-address` (10.44.18.23, which the instruction never states); `check`
  (hostalive / ping / icmp); `down-time` (06:52, derived from the epoch, with a note);
  `stale-config` (derived: old / pre-move address, not updated, monitoring configuration, update
  the address, false alarm, ...).
- Count: `hours-down` 28 (nouns hours/hrs/h, window 3; "28h", "1 day 4 hours" ... in
  `extra_any_of`), derived from the epoch and the stated now.
- Forbidden: `real-outage` ("is a real outage", "the host is really down", "go ahead with the P1",
  "raise the P1 with the network team", ...); `checks-new-address` ("icinga is checking
  10.44.30.23", "icinga uses 10.44.30.23", ...). No `attributed_to`. The forms
  "icinga is pinging/pings 10.44.30.23" were dropped because they contain the required form
  "ping" (fact-entanglement). Polarity checked: "This is not a real outage", "Is the host really
  down? No.", "Real outage: No", "Icinga is not checking 10.44.30.23" and "Don't raise the P1 with
  the network team" are not hits.
- Floors: mute 0.429, nocall 0.229, fabricate 0.200 (max per-fact 0.314, below mute).

## The wrong answer

"Icinga is checking sftp-edge-cph-04 with a hostalive ping and it has been hard DOWN since 06:52
UTC ... (28 hours now) ... this is a real outage at the network layer. Go ahead and raise the P1
with the network team." (`/tmp/ext/scratch/icinga-218-220/a/219-wrong.md`). Reward 0.771: answer
0.714. It misses `stale-config` and trips `real-outage`, but it banks the address, check, time and
duration it read correctly. This is the accepted bar-C residual (true literals plus a false
conclusion earn partial credit; `docs/ops/bench-authoring.md`, the bench-h4 acceptance bar). A
fabricator that also claims Icinga checks 10.44.30.23 scores 0.543.

Two fresh honest answers (terse prose; and `Key: value` lines with "Real outage: No" and an
explicit denial that Icinga checks 10.44.30.23) both score 1.000.

## Invented

The hosts, addresses, VLAN move, groups, vars and epochs are invented for this task. Nothing comes
from bench-v4 or from production data.
