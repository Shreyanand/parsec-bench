Finance is costing my etcd tuning lab on the Babylon cluster `fulmar`: ResourceClaim
`ocp4-etcd-perf-lab-k3dzr` in namespace `user-tkariuki-redhat-com`. A colleague sized its
worker pool from the component definition of the catalog item it came from, but I picked
non-default options when I ordered it, so I doubt that's right.

Look up that ResourceClaim. How many worker nodes does my lab actually have, and what
instance type? Then, for comparison: what does the catalog default specify for workers
on fulmar, type and count?
