# bench-v5-icinga-202-flapping-recovery-is-not-resolution

**Kind:** trap. **Services:** icinga. **Calls:** 1. **Weights:** 0.2 / 0.8.

## What it measures

Whether "it went green by itself" gets read as resolution. `haproxy-backend-api` on
`edge-lb-sjc-2` is `state` 0 and its output says OK, but `flapping` is true, and
`flapping_current` 41.7 is above `flapping_threshold_high` 30. Icinga2 suppresses
notifications for a flapping object, so the quiet since 09:12 is not evidence of a fix. The
agent must say that the service is flapping, that the ticket should stay open, and why the
silence is misleading. It must also hand over the one other open problem on the host, the
`tls-handshake` WARNING.

## Grounding

- api.json `/query_icinga`: `get_services` reads only `services`. The `host` filter is exact
  on `attrs.host_name`, and the rows come back verbatim (SKILL.md Derivation Rules).
- `attrs` is a free object in schema.json. `flapping`, `flapping_current`,
  `flapping_threshold_low`/`_high`, `enable_flapping`, `last_state`, `last_state_change`
  and `last_notification` are stored as Icinga2 names them.
- The forbidden actions `get_flapping_status` and `get_history` are neither enum values nor
  aliases, so the simulation returns `Unknown icinga action: ...`.
- Validator WARN, justified: the golden `result` is the documented JSON serialization of the
  seeded rows, which the leaf-level grounding check cannot match. The same WARN appears on
  training 045/046.

## Contract

- Expected call: `get_services` with `host: edge-lb-sjc-2` (given in the instruction).
- Required: `flapping`; `keep-open` (the verdict); `notifications-suppressed` (derived:
  Icinga2 semantics, not stated in any field); `other-open` (the `tls-handshake` sibling).
- Count: `flap-current` 41.7 ("41.7%" accepted without a noun).
- Forbidden: `says-safe-to-close` ("safe to close", "is resolved", "has recovered", ...).
  `attributed_to` holds only phrases that specifically refute or attribute this claim (see
  tests/expected.json). Generic words ("not", "only", "will", ...) are not used. The probe
  `.scratch/probe/202.md`, an asserting sentence that also contains a negation, is hit.
- Weights 0.2 / 0.8. Mute floor 1/6 = 0.17.

## The wrong answer

"Yes, that's reasonable ... recovered ... resolved and you can close the ticket. The only
other thing is the TLS handshake latency WARNING" (`.scratch/wrong/202.md`). Reward 0.33:
answer 0.17. The only point it earns is for naming the TLS sibling. It misses flapping,
keep-open, suppression and the count, and it hits the forbidden fact.

## Invented

The host, services, outputs, address, group, percentages and epochs are invented for this task.
Nothing comes from bench-v4 or from production data.
