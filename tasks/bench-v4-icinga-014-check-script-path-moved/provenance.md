# bench-v4-icinga-014-check-script-path-moved

## What it measures

A chain that breaks in the middle and has to be recovered: the alert names a plugin
path, that path 404s in the repository, and the script is actually somewhere else. The
agent has to find it, read it, and then name the real fault — which is the check's
configuration, not the thing being checked.

The last part is the discriminating one. An UNKNOWN from a missing plugin says nothing
about IPA's health, and an agent that reports a broken replica has invented a finding.

## Grounding

`vendor/parsec/src/tools/icinga.py:97-104` for `get_services`. The
`/home/icinga/monitoring-scripts/...` plugin-path prefix is the shape real Icinga check
commands take in the trajectories, and the `IPA HEALTHCHECK on replica3.ops...` alert
is one a real 7-call trace investigates.

The failed `fetch_github_file` result is the real error string from the corpus's 13
path failures, so the golden path's second call is a faithful stand-in for what the
simulation returns.

## Why the golden path fetches the stale path first

The golden call sequence deliberately includes the **failing** fetch before the search.
That is the honest reference solution: the instruction says to try the path the output
names, and discovering it is absent is what motivates the search. `tool_calls.match` is
`ordered-subsequence`, so the failing call is not in `expected` — an agent that skips
straight to the search is not penalised — but the golden transcript shows the work.

## Weighting

`0.3 / 0.7`. The service and repository are given; the recovery is the agent's own, and
the answer carries the diagnosis plus a value that only the relocated file holds.

## Invented

Both script paths, the script body, the lag thresholds 300 and 900, the search matches
and the host name. **Nothing comes from the gitignored trace export.**
