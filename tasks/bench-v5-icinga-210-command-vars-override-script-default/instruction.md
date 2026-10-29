Disagreement on the team about the `repl-lag` alert on Icinga host `mysql-ro-lon-3`. One
engineer says it's a false alarm: the plugin `plugins/db/check_repl_lag.py` in
`rhpds/rhdp-monitoring` only goes critical at 600 seconds by default, and the replica is
"only" 340 seconds behind. The Icinga command definitions are in
`icinga/conf.d/commands/db.conf` in the same repo. Settle it: with which warning and critical
thresholds does Icinga actually run this check on that host, and is the alert legitimate?
