Every catalog item started failing on controller `east` right after a
configuration change went out. Job `90451` is one of them.

Read that job's log, find the agnosticv pull request behind the change, and read
the governor defaults that the job is complaining about.

Tell me the root cause and the mechanism. Name the configuration field the
governor still reads and the field that replaced it, say which pull request
introduced the change, and say what part the failing tests played.
