It is 2026-11-17 at 09:30 UTC. Icinga is warning about HTTPS certificate validity on `wiki-ber-01` and
`jira-ber-02`. Our AAP2 job template `tls-cert-renew` on controller `west` runs every Monday at
01:00 UTC and renews every certificate that is within 30 days of expiry.

Did the run of 2026-11-17 renew both certificates? For each of the two hosts, give me the expiry
date Icinga reports now. For any host that run did not renew, tell me what the job record shows
for that host, and what has to happen before its certificate expires.
