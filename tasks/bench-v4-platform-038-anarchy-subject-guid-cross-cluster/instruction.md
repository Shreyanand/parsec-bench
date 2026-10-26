A teammate wants a status check on their Babylon environment with GUID
`kx8vn`. They think it was ordered on the `south` cluster, but we run more
than one Babylon cluster and they are not certain.

Locate the AnarchySubject that belongs to this GUID, say which cluster it is
actually on, and report its current state and its desired state.

Then fetch the component definition of that subject's governor from the
cluster the subject is on, and report the number of instances that component
expects and the cloud provider it targets.
