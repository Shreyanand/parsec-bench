# bench-v5-icinga-210-command-vars-override-script-default

**Kind:** trap. **Services:** icinga, github. **Calls:** 3. **Weights:** 0.3 / 0.7.

## What it measures

Resolving threshold precedence across three sources that disagree. The alert says "340 s >
crit 300 s". The plugin `plugins/db/check_repl_lag.py` defaults to `--warning 300 --critical
600`, which is what a teammate cites to call the alert false. The CheckCommand
`mysql-repl-lag` in `icinga/conf.d/commands/db.conf` passes `--warning $repl_lag_warn$
--critical $repl_lag_crit$` whenever the service sets those vars. The `repl-lag` service row
sets `repl_lag_warn` 120 and `repl_lag_crit` 300. The effective thresholds are therefore
120 / 300, and the alert is legitimate. The warn value 120 appears only in the service vars
and the perfdata, not in the alert text or the script, so reading the Icinga row properly
is required.

## Grounding

- icinga: `get_services` with `host` returns `services` rows verbatim, including
  `check_command`, `vars` and `last_check_result.performance_data` (SKILL.md Derivation
  Rules; `attrs` is free-form).
- github: both files are seeded under `HEAD` and `main`. `fetch_github_file` resolves an
  omitted ref to the default branch. The golden calls omit `ref`.
- The CheckCommand uses real Icinga2 DSL (`arguments`, `set_if`, `macro()`), so the
  precedence the answer states is Icinga2's actual behaviour.
- No forbidden calls (not one of the group's eight).
- Validator WARN, justified: golden call 0 returns the documented serialized `result`
  string.

## Contract

- Expected calls, `unordered-subset`: `get_services host=mysql-ro-lon-3`, and
  `fetch_github_file` of both paths. All three arguments are given in the instruction, so
  they have no dependency on each other.
- Required: `legitimate` (verdict); `vars-mapping` (`repl_lag_crit`/`$repl_lag_crit$`, found
  only in the conf and the service row); `defaults-only-fallback` (derived).
- Counts: `effective-warn` 120 (vars only); `effective-crit` 300.
- Forbidden: `calls-it-false` ("is a false alarm", "threshold mismatch", "critical is 600",
  ...). `attributed_to` holds specific attribution phrases only ("engineer says", "the claim
  that", "by default", "defaults to"). A probe sentence that asserts the claim with a
  negation elsewhere is still hit (`.scratch/probe/210.md`).
- Mute floor 1/6 = 0.17.

## The wrong answer

"The engineer is right ... threshold mismatch ... the alert is misconfigured and the critical
threshold is 600 seconds" (`.scratch/wrong/210.md`). Reward 0.42: answer 0.17. It earns only
the 300 count, from quoting the default warning value next to "critical".

## Invented

The host, services, vars, script, CheckCommand file, outputs and epochs are invented for this
task. Nothing comes from bench-v4 or from production data.
