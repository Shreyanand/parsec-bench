# bench-v4-cloud-025-gcp-project-status

## What it measures

A single-call lookup where the finding is a *state* and the value of the answer is
connecting that state to the reported symptom. Reading `DELETE_REQUESTED` off the record is
easy; saying that it is why nothing can be deployed, and that the fix is a new sandbox
rather than anything inside this project, is the part being measured.

## Grounding

`get_project` is one of the two actions `sim-specs/cloud/openapi.json` declares for
`query_gcp_projects`, and the question is a real trajectory's verbatim shape ("whats going
on with GCP project openenv-jbfsp"). Two real `get_project` calls appear in the corpus.

The generated `schema.json` requires `project_id`, `name`, `state`, `create_time` and
`labels` on `GcpProject`, with `labels` as an object — which is why the GUID and owner facts
come from inside `labels` rather than from top-level fields, and why reading them is a
slightly different operation from reading `state`.

The `openenv-<guid>` project naming and the `conan` label are RHDP conventions the tool's
own schema carries.

## The neighbouring project

The seed holds a second `openenv-*` project owned by the same person and in state `ACTIVE`.
An agent that matches loosely, or reports the first row, gets the state wrong — and
`wrong-state-claim` forbids the assertions that follow from it. The bare word `ACTIVE` is
deliberately **not** forbidden: it is a seed literal on the other row, so an honest answer
may mention it.

## Weighting

`0.2 / 0.8`. One call whose only argument is in the instruction. Five answer facts, one of
them a judgment.

## Invented

Both projects, the GUID `wq4mt`, the owner `dmoreau`, the folder id and every timestamp.
**Nothing comes from the gitignored trace export** — the question's shape came from there;
the project in the real trace was a different one.
