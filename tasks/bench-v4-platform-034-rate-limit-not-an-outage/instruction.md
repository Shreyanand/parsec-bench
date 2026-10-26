A bulk cleanup of rehearsal labs was kicked off on controller `east` and the
destroy jobs are failing. Someone has also noticed the AnarchyRun objects piling
up and is worried the cluster is running out of etcd space. Job `90461` is one of
the failures.

Find how many destroy jobs failed, read one job's log, and read the catalog
configuration for the item being destroyed.

Tell me the root cause and the mechanism. Name the AWS API being called and the
per-second limit it hit, say what in the configuration let so many jobs run at
once, and say how the AnarchyRun build-up relates to the failures.
