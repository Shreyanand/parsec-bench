Vision inference demo job 647219 on controller `west` sat for over half an hour waiting on a GPU MachineSet, then failed. We ordered this lab with GPU switched off, so I don't understand why it wanted GPU capacity at all. A teammate's answer is to give that wait more attempts.

Read the job log, then read the role template that renders the GPU MachineSet, in the repository the job ran from. Tell me what value the job actually received for the GPU switch, why GPU nodes were requested anyway, and what to change.
