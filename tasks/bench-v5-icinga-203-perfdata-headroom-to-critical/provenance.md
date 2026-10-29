# bench-v5-icinga-203-perfdata-headroom-to-critical

**Kind:** happy. **Services:** icinga. **Calls:** 1. **Weights:** 0.2 / 0.8.

## What it measures

Reading Icinga performance data. The WARNING row's output is deliberately terse ("POOL
WARNING - tank0 above warning threshold"). The numbers exist only in
`last_check_result.performance_data`, as `tank0_used=412GB;400;460;0;500`, which follows the
plugin perfdata convention `value;warn;crit;min;max`. To get headroom to CRITICAL (460 − 412 =
48 GB) and percent used (412/500 = 82.4 %), the agent has to parse that string and pick
the crit field rather than the max field. The service runs on two hosts. A search without
`host` returns both, and the agent must also report the OK one.

## Grounding

- `get_services` honours `search` and returns matching `services` rows verbatim (SKILL.md
  "Filtering rules", Derivation Rules). `objstore-pool` occurs only in the two matching rows'
  `name`, so the matched set is the same under exact, substring or fuzzy search. The display
  name ("ZFS pool tank0 usage") does not contain it.
- `performance_data` is stored as an array of strings, the shape Icinga2's
  `CheckResult.performance_data` has. `attrs` is a free object in schema.json.
- The forbidden actions `get_perfdata` and `get_metrics` are not enum values or aliases.
- Validator WARN, justified: the golden `result` is the documented serialized string, as in
  training 045/046. Every value inside it is a seed value.

## Contract

- Expected call: `get_services` with `search: objstore-pool`. The search term is pinned,
  because a host-filtered call would miss one of the two hosts.
- Required: `warning-host` (s3gw-ash-1); `other-host-ok` (s3gw-ash-2 stated as OK).
- Counts: `headroom-gb` 48 (derived from crit minus value); `pct-used` 82.4 (derived from
  value/max, accepts "82.4%" or "82%").
- Forbidden: `headroom-to-full` ("88 GB", which is 500 − 412).
  `attributed_to` holds only phrases that specifically refute or attribute this claim (see
  tests/expected.json). Generic words ("not", "only", "will", ...) are not used. The probe
  `.scratch/probe/203.md`, an asserting sentence that also contains a negation, is hit.
- Mute floor 1/5 = 0.20.

## The wrong answer

1. "The output does not give the usage numbers, so I can't say..." (`.scratch/wrong/203.md`).
   Reward 0.68: answer 0.6, both counts missed.
2. "it can grow another 88 GB" (`.scratch/wrong/203b.md`). Reward 0.68: the headroom count
   is missed and the forbidden fact is hit.

## Invented

The hosts, addresses, service names, pool name, perfdata values and epochs are invented for
this task. Nothing comes from bench-v4 or from production data.
