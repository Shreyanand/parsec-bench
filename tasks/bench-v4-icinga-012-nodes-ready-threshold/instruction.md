The Icinga service `ocp-prod-nodes-ready` on host
`infra-grafana-cluster-us-east-1` is in a WARNING state.

Get its detailed state, then read the check definition at
`clusters/ocp-prod/monitoring/nodes-ready.yaml` in the
`rhpds/rhdp-monitoring` repository.

Report the number of nodes the definition expects and the ready count
below which it warns. Then say how many more nodes would have to go
unready before the check turns critical.
