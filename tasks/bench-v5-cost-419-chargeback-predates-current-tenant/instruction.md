I run September 2026 chargebacks for our AWS sandbox pool. Finance's default rule is to
bill an account's whole month to whoever holds it at month end, and I want to sanity-check
that for the biggest bill before it goes out.

1. Use the cost monitor's breakdown by linked account for 2026-09-01 to 2026-09-30 to find
   the sandbox account that cost the most.
2. Pull that account's September spend from Cost Explorer. Its end date is exclusive, so
   query 2026-09-01 to 2026-10-01.
3. Look the account up in the sandbox account database to see who holds it now.
4. Check AAP2 for that holder's lab jobs to see when their lab was provisioned.

Tell me the account, who holds it now, and when their lab was provisioned. Then tell me
how much of September they should actually be billed, and how much should not go to them.
