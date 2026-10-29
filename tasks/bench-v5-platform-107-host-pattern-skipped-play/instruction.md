Quantum simulator lab provisioning is broken. Job 372861 on controller `east` died complaining that `bastion_ssh_key` doesn't exist. A colleague has a PR ready that gives that variable a fallback value so the job gets past it. I'd rather understand the failure before merging that.

Read the job log and work out why the variable was never set. Find what in the log actually explains it, open the config playbook that failed in the repository the job ran from, and tell me what the fix is. Cite the line to change as `owner/repo:path:line`.
