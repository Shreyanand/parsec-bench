# bench-v5-icinga-211-thresholds-file-never-deployed

**Kind:** chain breaks. **Services:** icinga, github. **Calls:** 4. **Weights:** 0.3 / 0.7.

## What it measures

A chain whose break *is* the finding. `queue-wait` on `ci-runner-pool-b` is CRITICAL (p90
wait 310 s, crit 240 s), and someone wants to buy more runners. The service's
`vars.plugin` leads to `plugins/ci/check_queue_wait.py`. That script reads per-pool
thresholds from `queue_wait.yaml` next to itself. If the file is absent it *silently* falls
back to `DEFAULT_WARN_S = 120` / `DEFAULT_CRIT_S = 240`. Fetching
`plugins/ci/queue_wait.yaml` returns the in-band not-found error, which is the break. A repo
search for `queue_wait.yaml` finds only `plugins/ci/queue_wait.yaml.example`. The correct
conclusion is that the CRITICAL fires against fallback defaults nobody chose. The fix is the
missing config, not runner capacity.

## Grounding

- icinga: `get_services` with `host` returns the rows verbatim, including `vars` and
  `performance_data` (`p90_wait=310s;120;240;0`, which agrees with the fallback values).
- github `fetch_github_file`: no `files` row for `plugins/ci/queue_wait.yaml` under any ref,
  so the documented in-band `{"error": ...}` is returned (`is_error: true` in the golden). The
  script and the example are seeded under `HEAD` and `main`.
- github `search_github_repo` reads only `repo_search_results` by exact `(owner, repo, ref,
  search)`. Rows are seeded under `HEAD` and `main` for `queue_wait.yaml`, `queue_wait` and
  `plugins/ci/queue_wait.yaml`, all returning the single `.example` match, so the obvious
  phrasings work.
- No forbidden calls (not one of the group's eight).
- Validator WARN, justified: golden call 0 returns the documented serialized `result` string.

## Contract

- Expected calls, `ordered-subsequence` (each depends on the previous one): `get_services` →
  fetch the script → fetch `plugins/ci/queue_wait.yaml` (the break) → `search_github_repo`
  (owner/repo pinned, `search` free). Any of the three seeded phrasings returns the
  `.example` match. An earlier version pinned `search: queue_wait.yaml` to dodge a
  leakage.py false positive, which the coordinator has since fixed.
- Required: `config-file`; `config-missing` (the forms "does not exist" / "doesn't exist" were
  dropped because training contracts share them; the generic "not found" and "is missing"
  were later bound to the config file as their subject — `yaml is missing`, `file not found`,
  `config was missing`, `fetch came back not found`, … — and `missing from the repo`, `404`,
  `is absent`, `no such file` and the `never created/deployed/committed` forms remain);
  `only-example`; `not-intended` (derived).
- **Weak discriminator (flagged):** to clear the hazard-12 entanglement with `plugin-missing`,
  `config-missing`'s required-form list was grown (bound to its subject, 133 forms), and it was
  re-tested against fresh honest panels (fix-up #7, 2026-10-13). Plugin-missing fabricators
  still score 0.700–0.900, and the fabricate and mute floors are exempt (see `## Floor
  exemption`).
- Count: `default-warn` 120 (script and perfdata only).
- Forbidden: `plugin-missing` (excused only by "plugin itself is present"); `buy-runners`
  (excused only by attributions to the requester: "someone wants to buy", "before buying").
  Probe `.scratch/probe/211.md` ("The plugin is missing from the repo, not the config.") is
  hit.
- Mute floor 2/7 = 0.29.

## The wrong answer

"... the runner pool is genuinely congested; you need more runners for pool-b", after two
calls (`.scratch/wrong/211.md`). Reward 0.25: answer 0.14, tool calls 0.5.

## Invented

The host, services, vars, script, example file, search rows, pool names, outputs and epochs
are invented for this task. Nothing comes from bench-v4 or from production data.

## Gate exemptions

- expected-call-underivable: fetch_github_file.path=plugins/ci/queue_wait.yaml — composed from two earlier results: the `get_services` row's `vars.plugin` is `plugins/ci/check_queue_wait.py`, and that script's docstring says thresholds are read from `queue_wait.yaml` "next to this file" (`CONFIG = Path(__file__).with_name("queue_wait.yaml")`), so the path is the plugin's directory `plugins/ci/` plus that file name; `fetch_github_file` returns only `content`, so no earlier result can carry the joined string literally (owner-approved 2026-10-13).

## Floor exemption

Weak discriminator, owner-approved 2026-10-13 and flagged in the baseline report: real fabricators that make the golden calls and blame a missing plugin score 0.700-0.900 (four of the five measured at 0.800-0.900), far above the mute floor (0.500), because they also state the example file, the defaults and 120 s; and mute itself sits at the 0.50 cap. The gate's fabricate probe scores below mute (0.300) only because of how the forbidden forms are worded, not because this contract scores fabrication below a content-free answer.
