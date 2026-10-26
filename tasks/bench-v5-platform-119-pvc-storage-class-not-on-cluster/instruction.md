The SAP HANA lab VM `hana-db01` in namespace `sandbox-j5wqc-sap-hana-lab` on the
OpenShift Virtualization cluster `ocpv-garnet` has never booted since it was ordered
on 2026-10-12. A teammate is sure the cluster's Ceph storage has run out of space and wants
to open a storage expansion request.

Look at the namespace's claims and at what storage the cluster actually offers, and tell
me why the VM's disk isn't being provisioned. If the claim is pointing at the wrong
storage, repoint it to the right one for me.
