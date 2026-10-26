A customer is about to run a long evaluation on our TimescaleDB metrics lab and asked whether
the lab protects their data. The lab installs the role `ocp4_workload_timescale_metrics` from
`agnosticd/agnosticd-v2`, and its settings are in
`ansible/roles_ocp_workloads/ocp4_workload_timescale_metrics/defaults/main.yml`.

Does the role set up scheduled database backups out of the box? If it does, tell me the
schedule and how long backups are kept. If it does not, tell me what the file says is holding
it back.
