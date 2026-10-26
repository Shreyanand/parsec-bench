# bench-v5-icinga-207-host-down-masks-service-alerts

**Kind:** happy. **Services:** icinga. **Calls:** 1. **Weights:** 0.25 / 0.75.

## What it measures

Causal collapse of an alert storm, found by the agent itself. One `get_problems` call
returns six non-OK rows:

- host `kvm-rack9-n04`, DOWN since 2026-11-18 03:15 UTC (hard, 100% packet loss);
- four of its services: `libvirtd` CRITICAL, plus `guest-count`, `ksm-sharing` and
  `raid-health` UNKNOWN. All four are check_by_ssh timeouts to the host's address, and all
  began one to three minutes after the host went down;
- `unbound-resolve` CRITICAL on `dns-cache-02`, a host that is UP.

The instruction names no host or service. The agent has to see that the host's DOWN state
explains its four service alerts. That gives 2 incidents, 5 of the 6 alerts explained by
one problem, the start time 03:15, and a duration of 6 hours as of the stated 09:15 UTC.

## Grounding

- `get_problems` reads `hosts` and `services` and returns every row whose `attrs.state` is
  not OK, ignoring all filters (api.json SIMULATION STORE AUTHORITY; SKILL.md Store reads).
  The golden result is the host row followed by the five non-OK service rows, in stored
  order. The two UP hosts and the two OK services (`unbound-cache-hit`, and `libvirtd` on
  `kvm-rack9-n05`) are excluded.
- Host `state` 1 = DOWN, service 2 = CRITICAL and 3 = UNKNOWN, following Icinga2 values.
  `last_state_change` is an integer epoch, returned unchanged.
- The forbidden actions `get_host_problems` and `list_unhandled` are neither enum values nor
  aliases (`list_problems` *is* an alias, so it is not forbidden).
- Validator WARN, justified: the golden `result` is the documented serialized string (as in
  training 045/046). Every value inside it is a seed value.
- History: an intermediate version used `get_hosts` with alerts pasted into the instruction,
  to dodge a leakage.py false positive on `{action: get_problems}`. The coordinator fixed
  leakage.py, and this version restores the approved design.

## Contract

- Expected call: `query_icinga {action: get_problems}`.
- Required: `root-host` (kvm-rack9-n04); `symptoms-not-faults` (derived);
  `independent-incident` (unbound-resolve / dns-cache-02); `since-time` (03:15).
- Counts: `incidents` 2; `alerts-explained` 5 (derived: host + 4 services, with "5 of the 6"
  accepted); `hours-down` 6 (derived, with "6 hours", "six hours", "6h" accepted).
- Forbidden: `no-collapse` ("6 separate", "5 incidents", ...); `faults-in-services`
  ("libvirtd crashed", "RAID failure", ...).
  `attributed_to` holds only phrases that specifically refute or attribute this claim (see
  tests/expected.json). Generic words ("not", "only", "will", ...) are not used. The probe
  `.scratch/probe/207.md`, an asserting sentence that also contains a negation, is hit
  (answer 0.0).
- Mute floor 2/9 = 0.22.

## The wrong answer

"Icinga shows 6 problems, so 6 separate incidents ... libvirtd crashed ... possible RAID
failure ... The worst is libvirtd" (`.scratch/wrong/207.md`). Reward 0.42: answer 0.22. It
names the host and the DNS problem, but it misses the causal reading, the start time and all
three counts, and it hits both forbidden facts.

## Invented

The hosts, addresses, services, outputs, group names and epochs are invented for this task.
Nothing comes from bench-v4 or from production data.
