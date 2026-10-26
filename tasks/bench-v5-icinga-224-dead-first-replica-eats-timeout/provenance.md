# bench-v5-icinga-224-dead-first-replica-eats-timeout

**Kind:** trap. **Services:** icinga, github. **Calls:** 4. **Weights:** 0.3 / 0.7.

## What it measures

Whether the agent reconciles a plugin's own timing with Icinga's time budget, across three
Icinga records and the script. `ldap-bind` on `sso-broker-vie-2` is UNKNOWN with the Icinga 2 timeout
output `<Timeout exceeded.><Terminated by signal 9 (Killed).>`, and a colleague reads that as
"LDAP is timing out". The chain:

1. `get_services` for the host: `check_timeout` 30, `vars.ldap_servers` [ldap-vie-01, ldap-vie-02], and an
   execution window of exactly 30 s;
2. the plugin `plugins/idm/check_ldap_bind.py`: it tries the servers in order, `CONNECT_RETRIES` 2 x
   `CONNECT_TIMEOUT_S` 20 per server, starting from the first on every run, so a dead first
   server costs 40 s, more than the budget;
3. `get_hosts`: ldap-vie-01 DOWN since 07:05 UTC (seven minutes before the UNKNOWN), ldap-vie-02 UP;
4. `get_downtimes` for ldap-vie-01: a fixed host downtime since 07:00 UTC (CHG-60417, okarlsson), the
   replica retired and powered off, which is why nobody was paged for it.

So LDAP is up; the check is killed before it reaches the healthy replica. The fix is to remove
the retired server from `ldap_servers` (or reorder, or raise `check_timeout` above 40 s). The
trap is to page the IdM team for an outage that does not exist.

## Grounding

- icinga `get_services` with `host` (exact `attrs.host_name`); `get_hosts` with `search`
  (SKILL.md: `search` filters `get_hosts`; `host` is not honoured there, so the golden uses
  `search: ldap-vie`, which returns both replicas); `get_downtimes` with `host` (exact
  `attrs.host_name`; host-level and service rows). All rows verbatim. `check_timeout`,
  `execution_start` / `execution_end`, `last_state_change`, `fixed`, `is_in_effect`,
  `trigger_time` and `entry_time` are generic Icinga 2 attribute names; the timeout output is the
  string Icinga 2 itself writes when it kills a plugin. No value is shared with any task.
- github `fetch_github_file`: the plugin is seeded under `HEAD` and `main`.
- Derivability: the plugin path and both replica names are in the service row's `vars`.
- Forbidden calls: `reschedule_check` and `acknowledge_problem` are write actions the icinga
  bundle deliberately does not model (api.json `x-excluded-actions`), and the instruction says not
  to acknowledge or re-run anything.
- Leakage (`bench-leakage.py`, vs bench-v4 and vs the original bench-v5): no seed row, pinned call, instruction or answer-form finding. The only shared tokens are Python boilerplate (`python3`, `usr/bin/env`, `import`, `print`, `sys.exit`, `sys.argv`, `__name__`, `__main__`), the field names `last_state_change`, `is_in_effect`, `trigger_time`, the shared repo name `rhdp-monitoring`, the plain words `plugin`, `server(s)`, `replica`, `broker`, `seconds`, and `exceeded` / `killed` / `terminated` from Icinga 2's own timeout output. None is an identifier of any task.

## Contract

- `answer.fold_markup` is on, so backticks and bold around names in a markdown answer do not hide a form.
- Expected calls, `unordered-subset`: calls 2-4 each depend only on call 1, so their order is
  free. `get_services` (host pinned), the fetch (owner, repo, path pinned), `get_hosts` (action
  only; its `search` is free text), `get_downtimes` (host ldap-vie-01 pinned).
- Required: `second-server-fine` (ldap-vie-02 is UP / never reached; call 3 or the derivation),
  `replica-retired` (call 4 only), `fix` (derived recommendation).
- Counts: `check-timeout` 30 (call 1), `dead-server-cost` 40 (derived from the script, with a
  note; pair notations such as "2 x 20" in `extra_any_of`).
- Forbidden: `ldap-down`, claims only; `attributed_to` holds only refutations ("isn't down",
  "is not really down", "but it isn't"), for "your colleague says LDAP is down, but it isn't down". "ldap-vie-01 is down" is true and is not forbidden.
- Mute: 0.3 + 0.7 x 1/6 = 0.417. Nocall 0.117. Fabricate 0.300.

## The wrong answer

"The ldap-bind check is UNKNOWN because LDAP is timing out: the plugin cannot get a bind from the
directory within the 30 s check_timeout. ldap-vie-01 is down, and ldap-vie-02 is also down as far
as the check can tell, so this is an IdM directory outage. Page the IdM on-call." With the golden
calls it scores 0.417: tool calls plus the `check-timeout` count; the forbidden fact is hit and
the three required facts and the 40 s count are missed. Two fresh honest answers (prose;
`Key: value` lines denying the outage) score 1.000.

## Invented

The hosts, addresses, services, bind DN, change number, author, epochs and the plugin are invented
for this task. `rhpds/rhdp-monitoring` is the shared monitoring repository. Nothing comes from
bench-v4 or from production data.
