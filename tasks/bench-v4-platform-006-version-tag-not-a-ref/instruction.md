AAP2 job 90406 on controller east failed while resolving a base image.
Its log records the catalog item version the provision ran at.

Read the job log, then read
`ansible/configs/zero-touch-base-rhel/default_vars.yml` from the
`agnosticd/agnosticd-v2` repository on its default branch and report the
base image tag the configuration actually sets.

Say whether that tag matches the one the job reported as missing.
