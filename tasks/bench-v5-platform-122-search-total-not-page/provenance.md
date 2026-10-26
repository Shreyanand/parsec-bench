# bench-v5-platform-122-search-total-not-page

## What it measures

Two things, and only the second needs a file:

1. Reading a `search_github_repo` envelope correctly. The stored result for `service_mesh`
   in `agnosticd/agnosticd-v2` has 100 `matches`, `total_matches: 131` and
   `truncated: true`. The count is 131, and the list is incomplete.
2. A value only the fetched file supplies. Among the shown matches is
   `ocp4_workload_service_mesh_ambient/defaults/main.yml`. Its Istio version (v1.26.2) and the
   line that sets it (12) are graded, as a required fact and a citation with `line`.

Per the coordinator's note (122 and cost-403 are both truncation tasks), the graded
discriminators are split: the 131 count and the "incomplete" fact on one side, and the
version and its cited line on the other. A run that reads the envelope correctly but never
fetches still loses the version and the citation.

**Kind: trap.** Reporting the list length (100) as the repository's count.

## Grounding

- github SKILL.md "/search_github_repo": an exact (owner, repo, ref-or-HEAD, search) row
  returns the stored `matches`, `total_matches`, `truncated`. Derivation Rules:
  `total_matches` is the count before the 100-entry cap, and `truncated` says the cap applied.
  The seed honours `truncated = true ⇒ total_matches > len(matches)`.
- Seeded under `HEAD` and `main`. The 131 paths are 26 `ocp4_workload_service_mesh_*` roles ×
  5 files plus one doc, sorted, and the first 100 are stored as `matches` (the generator asserts
  the target file is among them).
- "/fetch_github_file": exact (owner, repo, path, effective ref). The defaults file is seeded
  under HEAD and main.
- leakage.py WARN: the weak literal `roles_ocp_workloads` is the real agnosticd-v2 directory
  name, environment vocabulary.

## Contract

- tool_calls (0.3), ordered-subsequence: `search_github_repo` {agnosticd, agnosticd-v2,
  search: service_mesh}, then `fetch_github_file` of the ambient defaults path.
- answer (0.7): required `truncated` (derived) and `istio-version`. Count `total` = 131.
  Citation `agnosticd/agnosticd-v2` + path + line 12. Forbidden `hundred-is-total`
  ("100 paths match", "there are 100 paths", "exactly 100", ...), excused only by phrases
  that name the cap ("only 100 of", "capped at 100", "returned only 100", "first 100").
- Probe: "There are 100 paths in total, not 131." hits `hundred-is-total`. "not" excuses
  nothing.

## The wrong answer

"The search ... matches 100 paths ... installs Istio 1.24 by default (defaults/main.yml)."
scores reward **0.30**: the truncation fact, version, count and citation are all missed, and
the forbidden fact is hit. The golden answer scores 1.0. Mute floor (validate.py): answer 0.20, reward 0.44 with golden calls.

## Invented

Every literal is invented: the 26 role names, the doc path, and the defaults file's content
and values. `agnosticd/agnosticd-v2` is the shared real repository (leakage.py ALLOW). Nothing
comes from bench-v4 or from production data.
