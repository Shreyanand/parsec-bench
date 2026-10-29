AAP2 job `90431` on controller `east` failed. The provisioning task that failed
retried ten times and then gave up with a read timeout, so the first read is that
something upstream was unreachable.

Work out the actual root cause. Read the job log, check whether anything else was
downloading from the same host during that window, and read the role's own defaults
to see how the failing URL is built.

Report the root cause with the specific mechanism, name the variables the URL is
composed from, say how many retry attempts were made, and give the root cause
category and your confidence.
