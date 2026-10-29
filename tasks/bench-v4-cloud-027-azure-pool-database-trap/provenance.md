# bench-v4-cloud-027-azure-pool-database-trap

## What it measures

Passing an argument whose valid values the **simulator will not enforce**. This is the
sharpest case in the suite for grading a trap in the contract rather than relying on the
environment.

`sim-specs/cloud/openapi.json` declares `database` with
`enum: ["pools", "aro", "roadshow"]` and `default: "pools"`, and it declares it *because*
parsec's implementation validates the value before dispatching. But that enum is a
**request**-shaped constraint, and `CLAUDE.md` limitation 11 records it in
`LOST_IN_GENERATION`: `harness-skills/parsec-cloud/schema.json` models the store, so the
enum reaches nothing the harness checks. The simulation will happily accept
`database: "prod"`.

Which means: if this scenario did not forbid the wrong values explicitly, an agent could
pass a value the real tool rejects, receive a plausible simulated answer, and score 1.000.
The contract is the only thing holding the line, and six wrong values are enumerated for
that reason.

## Why six forbidden entries

`prod`, `production`, `default`, `azure`, `subscriptions`, `main` — the plausible guesses an
agent reaches for when it has to name a database and has not read the enum. Enumerating them
is not elegant, and it cannot be exhaustive; it is what the contract format can express. The
`expected` call additionally requires `database: "pools"`, so a wrong value fails from that
side too even if it is not on the forbidden list. The two together are what make the trap
hold.

## The instruction states the three valid values

Deliberately. This is not a memory test about Azure pool databases — it measures whether the
agent passes an argument it was handed, which is the same thing
`bench-v4-platform-021` measures for `cluster`. An agent that ignores an explicitly stated
constraint would ignore it in production too.

## Weighting, and a structural cap worth knowing

`0.3 / 0.7`. It was first authored at `0.4 / 0.6` — the same as `bench-v4-platform-021`, and
for the same reason: one argument decides whether the call is legitimate at all. **The gate
refused it at floor_fabricate `0.400`**, and the number is not a coincidence: it is exactly
the tool weight.

That exposes a general constraint on authoring, not a quirk of this scenario. The fabricating
probe makes the **golden** tool calls and varies only the answer, so it earns the full
`tool_calls` component by construction. Its floor therefore has `weights.tool_calls` as a
hard lower bound, and with `FLOOR_FABRICATE_MAX = 0.35`:

> **A contract with any forbidden answer fact cannot carry a tool weight above 0.35.**

`-021` gets away with `0.4` only because it has no forbidden fact, so its fabricate floor is
`n/a`. This scenario has one and cannot.

Whether `0.35` is the right absolute cap for a probe that *did* make the correct calls is a
fair question — a fabricator has done the retrieval work, and the load-bearing check is the
comparative one (fabricating must not out-earn silence, which here it does not: `0.300`
against a mute floor of `0.417`). That question belongs to the suite-wide floor
recalibration, with the full distribution of thirty scenarios in hand. It is deliberately
**not** settled here, where the only motivation would be making this one scenario pass.

## Invented

Both subscriptions and the project tag. The `pool-01-NNN` subscription naming and
`projecttag` are conventions the tool's own schema carries; the generated
`AzureSubscription` requires only `id` and marks it `x-primary-key`, with `used` and
`projecttag` optional, so both seeded rows are minimal-plus-two. **Nothing comes from the
gitignored trace export.**
