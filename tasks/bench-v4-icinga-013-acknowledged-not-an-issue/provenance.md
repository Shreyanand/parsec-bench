# bench-v4-icinga-013-acknowledged-not-an-issue

## What it measures

Whether the agent will say "no". The alert is real, it is UNKNOWN, and the correct
answer is that nothing needs doing — because it is acknowledged, inside an active
downtime, and carries a comment explaining an expected monthly condition.

The instruction is deliberately framed the way a colleague would forward it, pasted
table and all, which is the shape a real trajectory took ("Is it actual[ly a
problem]?" against an UNKNOWN/ACKNOWLEDGED row).

## Why four required facts rather than one

A bare "no, it's fine" is not a good answer and a scenario that rewarded one would be
measuring agreeableness. `the-reason` and `ticket` both come **only** from the comment,
so the `get_comments` call has to happen and its content has to be read;
`suppression-state` requires reporting the acknowledgement and downtime that justify
the verdict. Together they make the verdict evidenced rather than guessed.

This also keeps the mute floor honest: with four required facts against one forbidden
one, an answer that asserts nothing collects a fifth of the answer weight rather than
half.

## Grounding

`vendor/parsec/src/tools/icinga.py:97-104` for the three actions. The seeded row uses
`acknowledgement: 1` and `downtime_depth: 1`, both within the enums the generated
`schema.json` declares for `IcingaService`, and `state: 3` is UNKNOWN.

The alert's subject — a Babylon schema YAML diff check failing on a GitHub API 401 —
is the shape of a real trajectory's input. Its explanation, the PAT rotation and the
Vault sync, is authored.

## Weighting

`0.2 / 0.8`. Three calls, all with the host handed over, none of them a discovery.
Everything being measured is the reading of what came back.

## Invented

The ticket `RHDPSUP-8812`, the comment text, the downtime, the PAT-rotation
explanation and every timestamp. `opentlc-mgr` is the conventional RHDP
administrative account. **Nothing comes from the gitignored trace export.**
