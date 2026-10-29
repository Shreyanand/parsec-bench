It is 2026-11-04 at 10:20 UTC. I'm deciding which On-Demand Capacity Reservations in
us-east-1 to release first, and I want to start where reserved capacity sits idle. Run AWS
Capacity Manager with its default 168-hour window, grouped by availability zone.

From that result, tell me:

1. the unused reservation cost in each zone, and the total across all of them;
2. how many zones hold reservations, and which zone wastes the most (with its figure);
3. our Terraform modules and runbooks address zones by name (us-east-1a, us-east-1b and so
   on), so give me the zone name of the worst one. That is where the release work starts.
