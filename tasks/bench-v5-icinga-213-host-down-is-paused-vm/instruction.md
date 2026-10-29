Students in a lab can't SSH to their bastion. Icinga host `lab-bastion-kx7q2` has been DOWN
since early afternoon on 2026-12-02 with 100% packet loss, and the network team insists nothing
changed on their side. The bastion is a VM on one of our OCP-V clusters; Icinga's record for the
host should tell you which cluster and namespace. Find out what is really wrong with it, and
whether the other VM in that lab is affected too.
