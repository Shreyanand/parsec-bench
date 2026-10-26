AAP2 job `47290` on controller `west` failed while provisioning the
`kestrel-api-lab` catalog item: a role in the job hit a variable that is not
defined. This lab's cluster has no Route 53 hosted zone, and we do not want to
give the role one.

Read the job's log, then read the role's defaults and the template the error
points to, in the repository the job ran from.
Tell me the exact name of the variable the error says is undefined.
Tell me which role variable decides whether the template uses that variable, and which value of it makes the template use it.
Tell me which variable I should set, and to what, so that this lab provisions without a hosted zone.
