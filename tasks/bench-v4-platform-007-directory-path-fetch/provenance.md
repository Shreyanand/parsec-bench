# bench-v4-platform-007-directory-path-fetch

## What it measures

Choosing the right tool for a directory. `fetch_github_file` fetches a file;
handing it a directory path fails with "Failed to get file contents. The path does
not point to a file or directory, or the file does not exist in the repository."
**13 real trajectory calls did exactly that**, the second most common failure
signature in the corpus after the wrong-owner 404. The correct move is
`search_github_repo` first, then fetch the path it returns.

The instruction states outright that the tree is a directory, so this is not a
knowledge test — it measures whether the agent acts on what it was told.

## Grounding

`vendor/parsec/src/tools/github_files.py` is the module whose error the observed
agent kept hitting; `search_github_repo` and `fetch_github_file` are both declared
in `sim-specs/github/openapi.json`, with `search` required on the former and `path`
on the latter.

Three forbidden call entries cover the directory at three depths — the tree root,
the role directory, and the role's `tasks` directory — because an agent narrowing
its way down hits the same error at each level and only the leaf is a file.

## Weighting

`0.3 / 0.7`. The repository and the role name are given, so neither call is a
discovery; what is measured is the order and the tool choice, plus two values that
only the file supplies.

## The forbidden answer form is narrow, deliberately

`directory-as-file` forbids claiming to have *read* the directory, not the directory
path itself — the instruction names that path, so quoting it is correct. As in
`-006`, the narrowing is safe because the wrong move is a call argument caught by
`tool_calls.forbidden` regardless of phrasing.

## A generated-schema constraint worth recording

`RepoSearchResult.matches` is an array of **plain strings** in
`harness-skills/parsec-github/schema.json`, not an array of objects. The first draft
of this seed used `[{"path": "..."}, ...]`, which reads naturally and is what a
response shape would suggest — the offline gate rejected all three rows with
`is not of type 'string'`. Read the generated schema, never the tracked spec, when
writing a seed.

## Invented

The role name `ocp4_workload_pipelines_operator`, the task file body, the three
search matches, and the retry and delay values. `ansible/roles_ocp_workloads` is
AgnosticD's real convention for that tree. **Nothing comes from the gitignored
trace export.**
