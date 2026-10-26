# bench-v5-icinga-205-notifications-disabled-nobody-paged

**Kind:** happy. **Services:** icinga. **Calls:** 1. **Weights:** 0.2 / 0.8.

## What it measures

Explaining why Icinga stayed silent from a per-object notification switch. `saml-cert-chain`
on `sso-idp-fra-01` has been hard CRITICAL since 2026-11-18 11:00. It has
`enable_notifications: false` and `last_notification: 0`, and it is neither acknowledged
nor in downtime. Its sibling `ldap-bind-latency` has notifications on, and a
`last_notification` overnight. That explains the instruction's "they did get paged for
something else". The agent must name the switch as the cause, show that no notification was
ever sent, identify the page that did go out, and work out the 19 hours in hard CRITICAL
as of the stated 06:00 UTC.

## Grounding

- `get_services` with `host` reads `services` filtered by exact `attrs.host_name` and returns
  rows verbatim (SKILL.md "Filtering rules", Derivation Rules).
- `enable_notifications`, `last_notification`, `last_state_change` and
  `last_hard_state_change` are Icinga2 Checkable attributes stored in the free-form
  `attrs`. The bundle's own db.json carries `enable_notifications` on services.
- The forbidden actions `get_notification_history` and `list_notifications` are neither enum
  values nor aliases.
- Validator WARN, justified: the golden `result` is the documented serialized string (as in
  training 045/046).
- Leakage WARN, justified: "06:00" is a clock time, not an identifier.

## Contract

- Expected call: `get_services` with `host: sso-idp-fra-01`.
- Required: `notifications-disabled`; `never-notified`; `sibling-page` (ldap-bind-latency);
  `re-enable` (derived remedy).
- Count: `hours-hard` 19. It is derived from `last_hard_state_change`, and `extra_any_of`
  accepts "19 hours", "19h" and "19 h".
- Forbidden: `wrong-suppression` (acknowledged / in downtime / pager / routing / escalation).
  `attributed_to` holds only phrases that specifically refute or attribute this claim (see
  tests/expected.json). Generic words ("not", "only", "will", ...) are not used. The probe
  `.scratch/probe/205.md`, an asserting sentence that also contains a negation, is hit.
- Mute floor 1/6 = 0.17.

## The wrong answer

"Icinga would have alerted, so the most likely reason is an escalation policy or routing
problem ... about 19 hours" (`.scratch/wrong/205.md`). Reward 0.33: answer 0.17. It gets
the duration right but misses all four required facts, and it hits the forbidden fact.

## Invented

The host, services, CA name, outputs, address, group and epochs are invented for this task.
Nothing comes from bench-v4 or from production data.
