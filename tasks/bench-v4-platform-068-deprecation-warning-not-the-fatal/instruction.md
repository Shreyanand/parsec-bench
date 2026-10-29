AAP2 job `61937` on controller `west` failed while provisioning the
`fleet-edge-lab` catalog item. Scrolling its log, I can see a deprecation warning
printed right before the fatal line, and I suspect that deprecated collection is
what broke the provision.

Read the job's log, then read the role's task file for the failed task in the
repository the job ran from.
Tell me which task failed.
Tell me which module that task calls.
Name the arguments the error says are missing.
Tell me whether the deprecation warning is the cause.
