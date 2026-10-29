Investigate the Icinga alert `aap2-job-status` on host
`aap2-prod-us-west-2`.

Get the service's detailed state and check for comments and downtimes.

The check script is `monitoring/aap2/check_job_status.py` in the
`rhpds/rhdp-monitoring` repository. Read it and report the window it
counts failures over, the warning threshold, and which job action it
ignores when counting.
