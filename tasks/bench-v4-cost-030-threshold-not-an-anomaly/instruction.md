The cost monitor fired for account `419283746501` covering 2026-06. Before
anyone opens an incident, work out whether this is actually an anomaly.

Read the monitor's `summary` endpoint for 2026-06-01 to 2026-06-30, then
establish a baseline: query AWS costs for 2026-06-01 to 2026-06-30, for
2026-05-01 to 2026-05-31, and for the same month a year earlier, 2025-06-01
to 2025-06-30. Also check the capacity manager for how much of the spend is
unused reservation.

Give a verdict -- expected seasonality, a legitimate new workload, or an
incident -- and the observed spend, the threshold it crossed, and the
overall utilisation figure that supports it.
