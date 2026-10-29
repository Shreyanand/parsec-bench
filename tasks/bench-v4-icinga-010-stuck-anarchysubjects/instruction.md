Investigate the Icinga alert `anarchy-stuck-subjects` on host
`babylon-ocp-prod-us-east-1`.

Get the service's detailed state, and check whether anyone has commented
on it or scheduled a downtime for it.

The check script is `monitoring/babylon/check_stuck_subjects.py` in the
`rhpds/rhdp-monitoring` repository. Read it and report the critical
threshold it uses, then say by how much the current value exceeds it.
