The LLM Fine-Tuning Workbench lab provisioned without trouble up to 2026-09-26, and
now orders fail. The latest is AAP2 job `4172093` on controller `east`. In August 2026 we
had InsufficientInstanceCapacity on the GPU workers, so the team assumes AWS is short of
GPUs again and wants to wait it out.

Check whether this is the capacity problem again. Read the job log, look the catalog
item up and read its configuration, and work out where the lab is being built and where
the lab's region comes from. Tell me the root cause, which change is responsible, and
give the root cause category and your confidence.
