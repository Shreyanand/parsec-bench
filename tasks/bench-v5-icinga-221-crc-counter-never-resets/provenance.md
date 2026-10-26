# bench-v5-icinga-221-crc-counter-never-resets

**Kind:** happy. **Services:** icinga, github. **Calls:** 2. **Weights:** 0.3 / 0.7.

## What it measures

Reading a check script to learn what kind of number an alert is built on. `nic-errors-ens2f1` on
`ceph-osd-yul-14` is CRITICAL with `rx_crc_errors=1520 (crit 1000)`. The service's `vars.plugin` leads
to `plugins/net/check_nic_errors.py`, whose docstring says the value is the raw kernel counter from sysfs: cumulative
since the driver initialised the interface, never decreasing, never a rate. Once over a
threshold the service stays there until the counter is zeroed, which on these hosts takes a
reboot or a NIC driver reload; an optics or cable swap does not reset it. The same
`get_services` read also returns the sibling `nic-error-rate-ens2f1`, OK at +0.0/min since
2026-12-04 15:25 UTC (25 minutes after the swap the user reports), which is the only evidence of
whether errors are still happening. The correct answer: the counter check measures a lifetime
total (1520 vs crit 1000), the errors stopped after the swap, and the check clears only on a
reboot or driver reload. The perfdata unit `c` (counter) also hints at it.

## Grounding

- icinga `get_services` with `host` (SKILL.md, "Optional inputs": exact `attrs.host_name`
  match; rows returned verbatim). Three rows: the counter check, the rate check and an OK
  heartbeat check. `last_state_change`, `performance_data`, `vars` and `check_command` are
  generic Icinga 2 attribute names that many tasks also carry; no value is shared.
- github `fetch_github_file` (SKILL.md: exact `(owner, repo, path, effective ref)`; an omitted
  ref resolves to the default branch). The plugin and the rate plugin are seeded under `HEAD`
  and `main`.
- The path is derivable: it is the counter row's `vars.plugin`.
- Leakage (`bench-leakage.py`, vs bench-v4 and vs the original bench-v5): no seed row, pinned call, instruction or answer-form finding. The only shared tokens are Python boilerplate (`python3`, `usr/bin/env`, `import`, `print`, `sys.exit`, `sys.argv`, `pathlib`, `__name__`, `__main__`), the field name `last_state_change`, the shared repo name `rhdp-monitoring`, and the plain words `plugin`, `kernel`, `sysfs`, `threshold(s)`. None is an identifier of any task.

## Contract

- `answer.fold_markup` is on, so backticks and bold around names in a markdown answer do not hide a form.
- Expected calls, `ordered-subsequence`: `get_services` (host pinned) then the fetch (owner,
  repo, path pinned; the path comes from the first result).
- Required: `cumulative` (script only), `rate-zero` (the sibling rate service, from call 1),
  `clears-on-reset` (script only). None of them is an absence, so none is derived.
- Counts: `crc-total` 1520 and `crit-threshold` 1000, both from the alert.
- Forbidden: `still-erroring`, written as claims; a correct denial ("the errors are not still
  happening") is excused by the verifier's polarity reading. `attributed_to` holds only refutations ("but they're not", "they have stopped"), for the honest "you might think the errors are still happening, but they're not" shape.
- No forbidden calls (a happy task).
- Mute: 0.3 + 0.7 x 1/6 = 0.417. Nocall 0.117. Fabricate 0.300.

## The wrong answer

"The check counts CRC errors on ens2f1 and currently reads 1520 against a critical threshold of
1000. The errors are still happening, so the new SFP is also faulty. Open the hardware ticket and
replace the NIC." With the golden calls it scores 0.533: both counts are earned, the forbidden
fact is hit, and `cumulative`, `rate-zero` and `clears-on-reset` are missed. Two fresh honest
answers (terse prose; a table that denies the faulty-SFP reading) score 1.000.

## Invented

The host, interface, services, outputs, figures, epochs and both plugin scripts are invented for
this task. `rhpds/rhdp-monitoring` is the shared monitoring repository both splits use. Nothing
comes from bench-v4 or from production data.
