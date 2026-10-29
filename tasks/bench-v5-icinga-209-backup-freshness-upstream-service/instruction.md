It's 2026-11-18, 04:40 UTC, and Icinga is paging about `wal-archive-freshness` on host
`pg-archive-01`. Before anyone starts poking at the archive box: work out what that check
actually measures (its plugin lives in `rhpds/rhdp-monitoring`, and the service's vars say
which file) and follow it to whatever is really broken. I also want the plugin's warning
threshold, and when the real failure started.
