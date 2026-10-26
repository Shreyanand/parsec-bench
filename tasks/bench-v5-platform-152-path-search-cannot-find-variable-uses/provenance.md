## What it measures

Whether the agent knows what `search_github_repo` searches. It filters the repository's
**path tree** by substring (parsec's own description: "Search a GitHub repo's entire file
tree for paths matching a substring"). It does not grep file contents. The user wants to
rename `ocp4_workload_model_registry_instance_name` and asks the agent to search for it to find every user.

- `fetch_github_file` on the role's defaults: the default is `lab-registry` (line 17), and
  the comment above it says `ocp4_workload_model_serving_lab` reads it too.
- `search_github_repo` for the variable name: `matches: []`, `total_matches: 0`. No path
  contains the name, which is all that result can say. The agent holds the counter-evidence
  in hand: the file it just read contains the variable, yet the search did not return it.

The trap is strong because the tool's own description adds "If it returns zero matches, the
item does NOT exist". That is true of a path and false of a variable. The honest answer: 0
matches, the search covers paths and not contents, so it proves nothing about usage; and it is
not safe to rename here alone, because the file names a second consumer.

**Kind: trap.** The empty search reads as "nothing else uses it, safe to rename".

## Grounding

- github SKILL.md "/search_github_repo": reads only `repo_search_results` by exact
  `(owner, repo, ref-or-HEAD, search)`; with no row, the empty success shape
  `matches: [] / total_matches: 0 / truncated: false`. The search row for the variable name is
  seeded empty under `HEAD` and `main`, so the result is the same whether or not the agent
  passes `ref`, and any other spelling of the search also returns the empty shape.
- "/fetch_github_file": `files` by owner/repo/path and effective ref; seeded under `HEAD` and
  `main`.
- Extra seed for an agent that follows the comment: search rows for
  `ocp4_workload_model_serving_lab` and `model_serving_lab` (three paths), and that role's
  `tasks/main.yml`, which uses the variable on line 5. Neither is graded or expected.
- Seed: `files` 4, `repo_search_results` 6.

## Contract

- tool_calls (0.3), unordered-subset (both calls are named by the instruction):
  `fetch_github_file` {owner, repo, path} and `search_github_repo` {owner, repo}. The search
  string is free text and unpinned (hazard 19).
- answer (0.7): required `default` (lab-registry), `line` (17, derived), `consumer`
  (model_serving_lab), `path-search` (derived: the search matches paths, not contents) and
  `not-safe` (derived). Count `zero-matches` (0, derived). Citation `defaults-file`
  (agnosticd/agnosticd-v2 + path, no line: an honest answer names the file more than once, and
  the matcher reads only the first; the line is the `line` fact). Forbidden `safe-to-rename`
  (excused only by conditionals that name the second role's update) and
  `search-proves-unused`.
- Items: 9. Mute 0.3 + 0.7 x 2/9 = 0.456.

## The wrong answer

"The default is lab-registry, set in agnosticd/agnosticd-v2 ansible/roles_ocp_workloads/ocp4_workload_model_registry/defaults/main.yml on line 17. The search for
the variable returned 0 matches, which confirms it is unused outside this role. It is safe to
rename it in this role alone." With the golden calls it scores reward **0.611** (answer 0.444): it earns the true literals (`default`, `line`, the zero count and the citation), misses `consumer`, `path-search` and `not-safe`, and hits both forbidden facts. That partial credit for true literals is bar C of the bench-h4 acceptance bar, a recorded residual. Three fresh honest answers (terse prose, bold key/value lines that deny "only used in this role", and one that says it is safe "only if you also update" the other role) score 1.000.

## Invented

Every literal is invented: the role names, the namespace, the database name, the variable and
its default, and the consumer role. `agnosticd/agnosticd-v2` is the real repository name
shared by both splits. Nothing comes from bench-v4 or from production data.
