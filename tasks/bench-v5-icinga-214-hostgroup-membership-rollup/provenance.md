# bench-v5-icinga-214-hostgroup-membership-rollup

**Kind:** happy. **Services:** icinga. **Calls:** 1. **Weights:** 0.2 / 0.8.

## What it measures

Rolling hosts up by Icinga hostgroup membership, which only the `attrs.groups` field carries.
The user names the hostgroup `kiosk-fleet-bdx` and asks for its member count, which members
are DOWN, and each down member's last check output. The store holds eight hosts. Five carry
`kiosk-fleet-bdx` in `groups` (kio-bdx-a01, a02, a03, b01, b02); two of them are DOWN:
`kio-bdx-a02` ("CRITICAL - 10.61.4.12: rta nan, lost 100%") and `kio-bdx-b01`
("CRITICAL - 10.61.4.21: no ARP reply"). `kio-bdx-c01` and `kio-bdx-c02` share the
`kio-bdx-` naming but sit in `kiosk-staging-bdx`, and `c01` is also DOWN. An agent that
selects the fleet by name prefix reports 7 members and 3 down; only reading `groups` gives
5 and 2.

## Grounding

- `get_hosts` reads only `hosts`, applies `search`/`filter_expr` when given, and returns stored
  rows verbatim (SKILL.md "Store reads", "Filtering rules", Derivation Rules). The golden call
  passes no filter, so it returns all eight rows; a `filter_expr` on groups would return the
  five members, which carry the same facts.
- `groups` is a declared `attrs` property of `IcingaHost` in api.json. Host `state` 1 is DOWN.
- Validator WARN (none raised); the golden `result` is the documented serialized string.

## Contract

- Expected call: `query_icinga` with `action: get_hosts` only. No filter is pinned
  (hazard 19: free-text filters are never pinned).
- Required: `down-a02`, `down-b01` (the two down members); `a02-output` (lost 100%);
  `b01-output` (no ARP reply; the decoy c01 says "TTL ran out in transit").
- Counts: `members` 5, `down-count` 2.
- Forbidden: `staging-host-counted`, claims such as "3 hosts are down", "3 of 5",
  "kio-bdx-c01 is in kiosk-fleet-bdx". No `attributed_to`. Polarity checked: "It is not the
  case that 3 hosts are down" and "kio-bdx-c01 is in kiosk-fleet-bdx? No." are not hits.
- Mute floor 0.314 (1 forbidden of 7 items), nocall 0.114, fabricate 0.200.

## The wrong answer

The name-prefix reading: "The Bordeaux kiosk fleet has 7 hosts ... 3 hosts are down ...
kio-bdx-c01: CRITICAL - TTL ran out in transit" (`/tmp/ext/scratch/bench-v5-icinga-214-hostgroup-membership-rollup/wrong.md`).
Reward 0.657: answer 0.571. It names both real down hosts and their outputs, but misses both
counts and hits the forbidden fact.

Two fresh honest answers (terse prose; and a key/value header plus table that explicitly
excludes c01) both score 1.000.

## Invented

The hostgroups, host names, addresses, outputs and epochs are invented for this task.
Nothing comes from bench-v4 or from production data.
