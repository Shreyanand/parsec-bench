# bench-v5-icinga-222-lag-check-runs-on-satellite

**Kind:** trap. **Services:** icinga, github. **Calls:** 3. **Weights:** 0.3 / 0.7.

## What it measures

Whether the agent checks *where* a check executes before believing its number. `pg-standby-lag`
on `pgsql-rep-ams-07` is OK at "replay lag 0 s" while the user's app sees hours-old data. Three reads
settle it:

- `get_services` for the host: the service carries `command_endpoint: icinga-sat-ams-2`, and its
  `last_check_result.check_source` is `icinga-sat-ams-2`; the sibling `pgdata-free` runs on the host
  itself, so the difference is visible by contrast;
- the plugin `plugins/db/check_pg_standby_lag.py`: it connects only to the local socket (no `--host` option), and when
  the server it reaches is not in recovery it reports 0 s and exits OK, silently;
- `get_services` for `icinga-sat-ams-2`: its `pg-ido` service says the local server is a primary holding
  the IDO database `icinga_ido`.

So the 0 s is the satellite's own primary reporting "no replay lag", and the standby's real lag is
unmeasured. The trap is to read 0 s / OK as "the standby is in sync" and blame the app.

## Grounding

- icinga `get_services` with `host`, twice (SKILL.md: exact `attrs.host_name` match; rows
  verbatim). `command_endpoint`, `check_source` (inside `last_check_result`),
  `last_state_change`, `check_command` and `vars` are generic Icinga 2 attribute names; Icinga 2
  records the executing endpoint in `check_source` and runs a check on `command_endpoint` when it
  is set. No value is shared with any task.
- github `fetch_github_file`: the plugin is seeded under `HEAD` and `main`.
- Derivability: the plugin path is the host row's `vars.plugin`; the satellite's name is its
  `command_endpoint` / `check_source`.
- Forbidden calls: `get_endpoints` and `get_zones` are not `query_icinga` actions or aliases
  (SKILL.md, "Required inputs"), so they return the unknown-action error; they are the invented
  actions an agent reaches for to inspect the Icinga topology. `get_services` on the satellite is
  the real route.
- Leakage (`bench-leakage.py`, vs bench-v4 and vs the original bench-v5): no seed row, pinned call, instruction or answer-form finding. The only shared tokens are Python boilerplate (`python3`, `usr/bin/env`, `import`, `print`, `sys.exit`, `__name__`, `__main__`, and the DB-API calls `conn.cursor`, `cur.execute`, `cur.fetchone`), the field name `last_state_change`, the shared repo name `rhdp-monitoring`, and the plain words `plugin`, `postgresql`, `satellite`, `standby`, `server`, `seconds`. None is an identifier of any task.

## Contract

- `answer.fold_markup` is on, so backticks and bold around names in a markdown answer do not hide a form.
- Expected calls, `unordered-subset`: the two `get_services` reads (each with its `host`
  pinned) and the fetch (owner, repo, path pinned). Calls 2 and 3 both depend only on call 1, so
  their order is the agent's choice.
- Required: `runs-on-satellite` (the endpoint name, call 1), `local-socket` (script),
  `ido-primary` (call 3 only), `not-in-recovery-zero` (script; "is a primary" also comes from
  call 3), `real-lag-unknown` (derived absence).
- Forbidden: `standby-in-sync`, claims only; a denial ("this does not mean the standby is in
  sync") is excused by polarity. `attributed_to` holds only refutations ("but it isn't",
  "isn't actually in sync"), for "Icinga makes it look in sync, but it isn't".
- Mute: 0.3 + 0.7 x 1/6 = 0.417. Nocall 0.117. Fabricate 0.300.

## The wrong answer

"The pg-standby-lag check runs the plugin plugins/db/check_pg_standby_lag.py against the
standby and reports replay lag 0 s, with warning at 60 s and critical at 300 s. The standby is in
sync with the primary, so replication is healthy. The stale figures must come from the reporting
app's own caching layer." With the golden calls it scores 0.300: tool calls only, the forbidden
fact is hit and all five required facts are missed. Two fresh honest answers (prose; `Key: value`
lines denying the in-sync reading) score 1.000.

## Invented

The hosts, satellite, services, outputs, epochs, addresses and the plugin are invented for this
task. `rhpds/rhdp-monitoring` is the shared monitoring repository. Nothing comes from bench-v4 or
from production data.
