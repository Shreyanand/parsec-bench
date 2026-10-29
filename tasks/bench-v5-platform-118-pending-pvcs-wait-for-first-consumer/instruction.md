Our storage dashboard has been showing three PersistentVolumeClaims stuck in `Pending`
for hours, all in the OpenShift Virtualization namespace
`sandbox-r7tbm-rhel-ha-cluster-lab`. That namespace holds a RHEL high-availability lab
that was pre-built on the night of 2026-10-11 for a training session at 09:00 on
2026-10-13, which has not opened yet. The lab's VMs
are created powered off and get started when the session opens.

Is something wrong with the storage there? Someone on the team suggested deleting the
Pending claims and recreating them; should we?
