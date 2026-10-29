# bench-v4-platform-006-version-tag-not-a-ref

## What it measures

A conceptual confusion the observed agent made repeatedly: treating a **catalog
item version** as a **git ref**. Seven real `fetch_github_file` and
`search_github_repo` calls failed with `could not resolve ref "<version>" as a
branch or a tag`, across four distinct version strings —
`zero-touch-prod-1.0.6`, `rhads-2.3`, `cnv-sap-end2end-rhel9-0.0.9` and
`cnv-ocpmulti-wksp-1.2.1`.

The instruction deliberately puts a version string in front of the agent (the log
records it) and then asks for a file on the **default branch**. Passing the version
as `ref` is the trap.

## Grounding

The failure signature is `vendor/parsec/src/tools/github_files.py`'s territory: a
`ref` that resolves to neither a branch nor a tag. The four version strings above
are the observed shapes, and the one used here follows that shape rather than being
copied from any of them — `zero-touch-prod-1.0.6` matches the AgnosticD
`<config>-<stage>-<semver>` convention and the config name it belongs to,
`zero-touch-base-rhel`, is the seeded one.

## Weighting

`0.3 / 0.7`. Both calls have their identifiers handed over, so neither is an
achievement; the discrimination is entirely in *how* the second one is made and in
the comparison the answer has to draw.

## A forbidden form that is deliberately narrow

`version-as-ref-claim` forbids `ref <version>`, `at <version>`, `branch <version>`
and `tag <version>` — **not** the bare version string. The instruction says the log
records the version, so quoting it is correct behaviour and forbidding it outright
would penalise the honest answer. Only the claim that it is a git reference is
wrong. This is the narrowing that CLAUDE.md limitation 8 warns is usually the wrong
move; it is safe here for a specific reason: the wrong move is a *call argument*,
caught by `tool_calls.forbidden` regardless of phrasing, so the answer-side form
does not have to carry the detection on its own.

## Invented

Job id `90406`, the guid `p3wqf`, the version `zero-touch-prod-1.0.6`, both image
tags, the log text, the `default_vars.yml` body and every timestamp. **Nothing comes
from the gitignored trace export** — the four observed version strings informed the
*shape* only.
