## What it measures

Following `sub_components` from a multi-component parent to the child that actually carries the answer. On `kite`, `get_component` for `ai-platform-bundle` returns `cloud_provider: none` and an **empty** `expected_instances`. It also returns `sub_components` naming `ai-platform.base-ocp` and `ai-platform.gpu-nodes`. A second `get_component` on `ai-platform.gpu-nodes` (kite) gives:

- the instance type, `g6e.12xlarge`
- the count, 4
- the agnosticv file, `ai-platform/gpu-nodes/common.yaml`

An agent that stops at the parent reports that the bundle requests no GPUs.

## Grounding

- platform SKILL.md `/query_babylon_catalog`: `get_component` reads `babylon_components` filtered by `cluster` and looks up the "resolved component `name`". It returns `cluster, name, cloud_provider, env_type, platform, expected_instances, definition` "plus `scm_url`, `scm_ref`, `agnosticv_repo`, `agnosticv_path`, `sub_components` when stored".
- schema.json: `sub_components` is "Referenced child components for multi-component items" (an untyped array). It is seeded as `{name, item}` objects, and `item` is the child's component name verbatim, so the second call's `name` is derivable from the first result.
- `cluster` is a free request string, and every row carries `cluster`. condor holds an older twin of the parent and of the GPU child (`release-2026.09`, 2 x g5.8xlarge). Cluster filtering keeps the twin out of kite lookups. The instruction says the clusters differ, so the twin's figures are wrong for this question.

## Contract

- Calls, `ordered-subsequence`: `get_component {cluster: kite, name: ai-platform-bundle}` then `get_component {cluster: kite, name: ai-platform.gpu-nodes}`. The second name comes only from the first result.
- Forbidden call: `query_babylon_catalog` `action: get_sub_component`. It is not an api.json enum value, and the in-band result is `Unknown action`. The instruction's "GPU part of that bundle" makes it a plausible guess.
- Required: the instance type `g6e.12xlarge` and the file `ai-platform/gpu-nodes/common.yaml`.
- Count: 4 GPU machines.
- No forbidden facts: the 0.4 tool weight keeps the mute floor at 0.00.
- Weights 0.4/0.6.

## The wrong answer

`.scratch/probe/133-wrong.md` stops at the parent: "requests no GPU instances ... ai-platform/bundle/common.yaml". It scores **0.20**: tool calls 0.5 (first call only), answer 0.

## Invented

The component names, paths, refs, instance counts and the clusters `kite`/`condor` are invented. `rhpds/agnosticv` is the real shared repository name, and the AWS instance type names are real vocabulary. Nothing comes from bench-v4 or production data.
