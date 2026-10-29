A user says their VM `rhel9-jumphost`, in namespace `sandbox-hq3vt-rhel9-vm-lab` on
the OCP-V cluster `ocpv07`, keeps dropping off. Check the VM first, but do not stop there.

Look below the VM, at the worker machines of `ocpv07` itself: does every MachineSet have
the replicas it wants ready, and is every Machine up? If a MachineSet is short of its
desired replica count, say how many of its replicas are ready out of how many desired.
Name any Machine that is not Running and give the phase it is stuck in.
