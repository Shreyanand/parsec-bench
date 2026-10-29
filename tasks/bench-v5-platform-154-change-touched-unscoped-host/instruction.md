Change CHG-61207 ran the Amsterdam NTP baseline on AAP2 controller `east` as job `8840317` on
2026-11-18. The change record scoped it to the five Amsterdam time servers, `ntp-ams-01`
through `ntp-ams-05`, and nothing else. For the post-change review, tell me:

1. Did the job finish cleanly?
2. Which hosts did it actually change, and what did it change on them? How many hosts did it
   change in total, and how many of the five in-scope servers were among them?
3. Did it modify anything outside the approved scope? If it did, roll that host back to how
   it was before the run.
