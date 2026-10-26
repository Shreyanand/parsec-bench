AAP2 job 90404 on controller east failed while creating a CNV inventory.

Read that job's log and report the message the failing task returned.
Then read the role task that produced it and explain what is wrong with
the value being passed through the `to_json` filter.

Cite the file you read as `owner/repo:path`, state the change that fixes
it, and give the root cause category and your confidence.

The failing task is in `roles/create_inventory/tasks/main.yml` in the
`agnosticd/cloud_provider_openshift_cnv` collection. Read it.
