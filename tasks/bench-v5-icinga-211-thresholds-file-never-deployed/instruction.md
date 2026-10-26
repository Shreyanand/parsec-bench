Icinga has had `queue-wait` on host `ci-runner-pool-b` CRITICAL since the afternoon of 2026-12-08,
and someone wants to buy more runners. Before we spend money, check how the plugin decides
what counts as critical. Its path is in the service's vars, and it lives in
`rhpds/rhdp-monitoring`. Follow wherever the plugin gets its thresholds from, and tell me
whether this CRITICAL reflects the thresholds the team actually intended.
