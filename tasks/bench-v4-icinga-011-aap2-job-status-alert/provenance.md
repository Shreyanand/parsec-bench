# bench-v4-icinga-011-aap2-job-status-alert

## What it measures

The shape B skeleton again, on a cross-domain alert: an Icinga service that reports on
AAP2 state. The answer has to come from the check script's own constants rather than
from the alert text, and one of those constants (`IGNORE_ACTIONS`) changes how the
number should be read.

## The facts that prove the GitHub leg happened

The alert output states the critical threshold (4) and the failure count (7), so
neither proves anything. `WINDOW_MINUTES` (60), `WARN_FAILURES` (2) and
`IGNORE_ACTIONS` (`destroy`) appear **only** in the script. All three are required, so
an agent that skips the fourth call loses three of five answer items.

## Grounding

The five accepted read actions are `vendor/parsec/src/tools/icinga.py:97-104`. The
`AAP2 Job status` display name and the `aap2-prod-us-west-2` controller-host shape are
attested in the trajectories, where one 10-call trace investigates exactly this alert.
The script's contents are authored.

The forbidden calls are the two actions `icinga.py:122` rejects and the observed agent
invented — not any non-enum action; see `bench-v4-icinga-017`.

## Weighting

`0.3 / 0.7`. Host, service and script path are all handed over, so the calls are not
discoveries; the answer carries five independent facts, three of which require the
second service.

## Invented

The failure count 7, the thresholds 2 and 4, `WINDOW_MINUTES = 60`, `IGNORE_ACTIONS`,
the script body and the script path. **Nothing comes from the gitignored trace export.**
