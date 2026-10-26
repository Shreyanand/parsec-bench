# bench-v4-cloud-024-guid-to-account

## What it measures

Inferring intent from a bare token. **The entire instruction is a five-character GUID**,
which is the shape six real trajectories take — prompts that are literally `jbfsp`,
`9z4ks`, `2t7js`, `khzhq`, `gvbpb`, `xfp5h` and nothing else.

## Why `asked_by` is the GUID itself

Every required fact cites `jbfsq`, because that is the whole instruction. This is the one
scenario in the suite where a fact cannot quote a clause, and it constrains what may be
required: only what a bare GUID can reasonably be read as asking. The sandbox it names, who
holds it, and the account it lives in are that; anything further would be scoring the agent
on volunteering detail nobody asked for, which is the verbosity trap `CLAUDE.md` records
from three v2 scenarios.

The golden answer ends by offering the obvious follow-ups rather than pursuing them, which
is the honest response to an under-specified prompt.

## The second account is the discriminator, and the forbidden forms are assertions

`sandbox2292` is available, unassigned, and has a neighbouring account id. An agent that
returns the first row of the result, or matches loosely, lands on it.

The forbidden forms therefore tie the GUID to the wrong sandbox or the wrong state
(`jbfsq is sandbox2292`, `jbfsq is available`, `is unassigned`) rather than naming the bare
identifiers. Forbidding `sandbox2292` outright was the first draft and the gate's
`forbidden-absent` check refused it: those literals are in the seed, so an honest answer
that mentions the other row as unrelated would have been penalised for thoroughness. Same
correction as `bench-v4-platform-018`.

## Grounding

`query_aws_account_db` takes no required arguments in
`sim-specs/cloud/openapi.json`, and 19 real calls in the trajectories use it that way,
returning the sandbox-account table for local filtering. The `sandbox<NNNN>` naming, the
`<name>.opentlc.com` zone, `conan_status`, and the `guid: <guid> / catalog: <item>` comment
shape are all conventions the tool's own schema carries.

## Weighting

`0.2 / 0.8`. One argument-free call. Everything measured is whether the agent worked out
what was being asked and read the right row.

## Invented

The GUID `jbfsq`, both sandbox accounts, the account ids, the owner `rrivers` and the
partner email domain. **Nothing comes from the gitignored trace export** — the bare-GUID
prompt *shape* is what came from there, and the GUID used here is not one of the six.
