# bench-v5-icinga-223-executed-plugin-not-the-shell-twin

**Kind:** trap. **Services:** icinga, github. **Calls:** 3. **Weights:** 0.25 / 0.75.

## What it measures

Finding the plugin that actually executed, when the repo holds two files of the same name. The
`open-files` service on `kafka-brk-zrh-5` is WARNING ("pid 2817 has 66355 open files, 81% of limit").
Its `vars` give only `plugin_name: check_fd_usage`; the instruction says the repo path is
unknown. A repo search for the name returns two matches, `plugins/jvm/check_fd_usage.py` and `plugins/legacy/check_fd_usage.sh`. Only the service's
`last_check_result.command` decides between them: Icinga ran
`/usr/lib64/nagios/plugins/rhdp/check_fd_usage.py --pid-file /run/kafka/server.pid`, a `.py`
taking a pid file. That script divides the process's open descriptors by its **soft** "Max open
files" limit and goes CRITICAL at `CRIT_PCT = 88`. The shell twin measures kernel-wide file
handles against the kernel maximum and goes critical at 95 by default. An agent that fetches
the first match by name, or the shell file, answers "81% of the system-wide limit, critical at
95%" and steers the user toward fs.file-max, the wrong knob.

## Grounding

- icinga `get_services` with `host` (exact `attrs.host_name`; rows verbatim). `command` inside
  `last_check_result` is the generic Icinga 2 check-result attribute holding the executed
  command line; `last_state_change`, `check_command` and `vars` are generic attribute names too.
- github `search_github_repo` reads `repo_search_results` by exact `(owner, repo, ref, search)`
  (SKILL.md; an omitted ref resolves to `HEAD`). Rows are seeded under `HEAD` and `main` for
  six phrasings: `check_fd_usage`, `fd_usage`, `check_fd` (both matches), `fd_usage.py`,
  `check_fd_usage.py` (the .py only) and `check_fd_usage.sh` (the .sh only). An off-key
  phrasing returns `matches: []` (hazard 20); the plugin name from `vars` is the obvious key.
- github `fetch_github_file`: both scripts are seeded under `HEAD` and `main`, so fetching the
  decoy works and shows the decoy.
- Derivability: `plugins/jvm/check_fd_usage.py` appears in the search result.
- Forbidden calls: `get_check_commands` and `get_commands` are neither `query_icinga` actions
  nor aliases (SKILL.md, "Required inputs"); they are the invented actions an agent reaches for to
  look up the command definition behind `check_command`.
- Leakage (`bench-leakage.py`, vs bench-v4 and vs the original bench-v5): no seed row, pinned call, instruction or answer-form finding. The only shared tokens are Python and shell boilerplate (`python3`, `usr/bin/env`, `bin/bash`, `import`, `print`, `sys.exit`, `argparse`, `argparse.ArgumentParser`, `__name__`, `__main__`), the field name `last_state_change`, the shared repo name `rhdp-monitoring`, and the plain words `kafka`, `broker`, `kernel`, `process`. None is an identifier of any task.

## Contract

- `answer.fold_markup` is on, so backticks and bold around names in a markdown answer do not hide a form.
- Expected calls, `ordered-subsequence` (a chain): `get_services` (host pinned) →
  `search_github_repo` (only `repo` pinned; `search` is free text, and pinning owner too would
  make the call spec identical to bench-v4-icinga-014's and bench-v5-icinga-211's) → fetch of `plugins/jvm/check_fd_usage.py` (owner, repo, path
  pinned).
- Required: `executed-file` (the .py path), `soft-limit` (script only), `per-process`
  (script; partly guessable, and kept because the decoy reading denies it).
- Count: `crit-pct` 88 (script only; the command passes no `-c`).
- Forbidden: `kernel-wide-denominator`, every form anchored to "81%" or to "measured against",
  so an honest answer that describes the shell twin ("the .sh measures kernel-wide handles")
  does not trip it. No `attributed_to`. The shell twin's critical default (95) is not forbidden:
  an honest answer may quote it, and `crit-pct` already fails a 95 answer.
- Mute: 0.25 + 0.75 x 1/5 = 0.400. Nocall 0.150. Fabricate 0.250.

## The wrong answer

"The plugin is plugins/legacy/check_fd_usage.sh. It reads /proc/sys/fs/file-nr, so the 81% is
of the system-wide file handle maximum, and it goes CRITICAL at 95%. Raise fs.file-max on the
broker host." With the golden calls it scores 0.250: tool calls only; every required fact and
the count are missed, and the forbidden fact is hit. Two fresh honest answers (prose that
dismisses the shell twin; a table that denies fs.file-max) score 1.000.

## Invented

The host, services, pid, figures, epochs, the deploy path and both scripts are invented for this
task. `rhpds/rhdp-monitoring` is the shared monitoring repository. Nothing comes from bench-v4 or
from production data.
