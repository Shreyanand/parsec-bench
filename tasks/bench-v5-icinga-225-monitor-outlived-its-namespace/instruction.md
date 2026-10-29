Icinga has been paging us about `lab-ws-n3v8d` since the evening of 2026-12-05: the host is DOWN and
so are checks on it. It's a student workstation VM on one of our OCP-V clusters, and Icinga's
host record says where it lives. Tell me where Icinga thinks it lives, and find out what state
the VM is in. Labs sometimes get moved between clusters, so if it isn't where Icinga says, check
whether it exists anywhere else. If it has simply stopped I'll start it myself, so don't try to
change anything. Also tell me how many of the host's service checks are failing, and what we
should do about the pages.
