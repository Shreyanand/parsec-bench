I'm planning a firmware update on OpenShift Virtualization worker `tarn-wrk-06` (cluster
`ocpv-tarn`) for 2026-11-19 at 22:00 UTC. The only tenant with VMs on that node is the escrow
team, namespace `fin-escrow-prod`. I want to use our AAP2 template `ocpv-node-maintenance`, which
cordons the node and live-migrates its VMs to other workers. It did exactly that for `tarn-wrk-03`
in job 5530718 on controller `east`, and the CRM team never noticed.

Can the escrow team expect the same on tarn-wrk-06? Tell me which of their VMs are running on it.
For any VM that can't be moved live, give me the claim that keeps it there, that claim's access
mode and its storage class, and what we have to do with that VM instead. Also tell me how many VMs
job 5530718 moved and why it had no trouble. If every VM can move, start the template for
tarn-wrk-06.
