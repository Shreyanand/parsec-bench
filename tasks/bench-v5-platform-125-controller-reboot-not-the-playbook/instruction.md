AAP2 job `6907233` on controller `west` failed on the night of 2026-10-07 while
provisioning the event streaming lab. A teammate scrolled the log, saw it stuck retrying
"Wait for the Kafka cluster to report Ready", and is convinced the
`ocp4_workload_amq_streams` role is broken. They're about to start rewriting it.

Before they do, find out why the job actually failed. The west controller is monitored
in Icinga as host `aap2-ctl-west-01.mgmt.example.net`; check whether anything was
scheduled on it around that time. Tell me what happened and what we should do. If something
was, tell me who scheduled it.
