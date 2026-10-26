# bench-v4-platform-018-find-jobs-window

## What it measures

Four discriminating arguments in one call. The seed is built so that **each** of the
three filters, if dropped, produces the same wrong count of 4 — one extra job for the
wrong controller, one for the wrong date range, one for the wrong status. The value 3 is
reachable only with all three applied.

That is what makes a single-call scenario worth a `0.5` tool weight: the call is the
whole exercise, and the answer is close to a direct read of its result.

## The seed is adversarial by construction

| job | why it is excluded |
|---|---|
| `90414` | same template, same range, **controller west** |
| `90415` | same template, same controller, **before the range** |
| `90413` | same template, same controller, in range, **successful** |

Each is excluded by exactly one filter, and the count fact is what catches a dropped
one: every single dropped filter yields 4 rather than 3, so `failure-count` fails.
`earliest-id` adds a second, sharper check on the date filter specifically — `90415` is
genuinely the earliest failure *in the seed*, and only the range makes `90410` the right
answer.

## Why this scenario has no forbidden fact

It was first authored with one, forbidding the three out-of-scope job ids. The gate
refused that outright: `forbidden-absent` reported that those ids are in a declared
service's seed, so **the trap was defused** — an honest answer that explains what the
filters excluded would name them legitimately and lose a point for being thorough. That
is a false negative against a better answer, so the fact is gone rather than reworded.

Nothing is lost. Every dropped filter still produces a count of 4 and fails
`failure-count`, and `earliest-id` still localises the date filter. The scenario reports
`n/a` for the fabricate floor, which is correct and not a gap: with a purely positive
contract there is no invented outcome to model.

## Grounding

`find_jobs` is one of the four actions `sim-specs/platform/openapi.json` declares for
`query_aap2`, and `controller`, `template_name`, `status`, `created_after` and
`created_before` are its declared arguments. 23 real `find_jobs` calls appear in the
trajectories, one trace narrowing progressively through exactly these arguments across
three successive calls — this scenario asks for the narrowed form directly.

`status: "failed"` is one of the five values the generated `schema.json` allows on
`Job.status`. All five are present in the v3-era bundle; the two-value truncation that
motivated the parsec-grounded rebuild is gone.

## Absolute dates, and why they are safe here

The instruction names `2026-05-01` and `2026-05-21` explicitly rather than saying "in
the last three weeks". Absolute dates in both the instruction and the seed mean the
correct answer is the same whenever the suite runs, which is the whole point of the
wall-clock rule.

## Weighting

`0.3 / 0.7`, arrived at the same way `bench-v4-platform-005` was.

The argument for `0.5 / 0.5` is real — one call, four arguments, each of which changes the
answer — and that is how this was first authored. **The gate refused it:** floor_mute
`0.625` against a maximum of `0.50`, floor_fabricate `0.500` against `0.35`. This is the
second scenario in the suite to hit it, and the mechanism is the same both times: with a
forbidden fact present, a `0.5` tool weight hands a mute agent more than half the reward,
because the forbidden fact is banked by silence. A forbidden fact and a high tool weight
compete for the same headroom.

The fix followed the rule: the instruction now asks for **every** failing job id rather
than only the earliest, which added two required facts and made the scenario harder, and
the tool weight came down to 0.3. No threshold was moved.

## Invented

All six jobs, their ids in the reserved 90000-99999 range, their guids and every
timestamp. **Nothing comes from the gitignored trace export.**
