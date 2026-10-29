Kafka broker `kafka-brk-zrh-5` has had its Icinga `open-files` check in WARNING at 81% since the
afternoon of 2026-12-08. Before I choose between raising the broker unit's LimitNOFILE and
raising the kernel's fs.file-max, I need to know what that 81% is a share of, and at what
percentage the check turns CRITICAL. The plugin is somewhere in `rhpds/rhdp-monitoring`, but
I don't know its path there; tell me which file in the repo is the one Icinga actually runs.
