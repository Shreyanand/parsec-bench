AWS sent us a scheduled-retirement notice for EC2 instance `i-0b6d2f8e4c1a9735e`: the
host under it will be retired on 2026-11-24 at 04:00 UTC. The instance is part of our
OpenShift Virtualization cluster `ocpv-larch`. Before I plan the drain, tell me:

1. Which OpenShift node and which Machine that instance is.
2. Which MachineSet owns that Machine, and how many other Machines in the same MachineSet
   could take over its workloads while it is being replaced.
3. How many of the cluster's Machines, control plane included, run in the same
   availability zone as that instance. AWS sometimes retires hardware in batches per zone.
