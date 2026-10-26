AAP2 job `58204` on controller `east` failed on an undefined variable while
provisioning the `edge-mirror-lab` catalog item. The variable name in the error
looks misspelled to me, and my suspicion is that the misspelling is in the
role's task file.

Read the job's log, then read the role's task file for the failed task in the
repository the job ran from.
Tell me the exact variable name the error says is undefined.
Tell me whether that exact name appears in the task file.
Tell me which variable the failing task passes as its registry credential, and through which option.
