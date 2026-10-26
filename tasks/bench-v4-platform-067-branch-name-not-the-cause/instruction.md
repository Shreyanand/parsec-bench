AAP2 job `90687` on controller `east` failed while provisioning the
`gitops-canary-lab` catalog item for an event. A teammate opened
`agd-v2/gitops-canary-lab/event.yaml` in the `agnosticd/agnosticd-v2`
repository, saw that it pins the deployer to an experimental feature branch, and
is convinced that branch broke the provision.

Read the job's log and its failed events, and read that `event.yaml`.
Tell me which task failed.
Name the secret the error says is missing, and the path it was looked up at.
Say which branch `event.yaml` pins, and tell me whether that branch is the cause.
