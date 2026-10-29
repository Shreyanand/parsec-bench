# Architecture

The benchmark measures **parsec**, a production Red Hat operations agent, on
questions whose answers live in backend systems: an AAP2 automation controller,
Splunk, OpenShift Virtualization clusters, the Babylon catalog, GitHub, Icinga,
cloud-provider APIs and their billing. None of those systems is reachable from a
benchmark. They are replaced by **LLM-driven simulations**, each grounded in
parsec's own tool code and seeded per task with a small, fully authored world.
parsec itself runs unmodified except for one redirect at its tool dispatch
point, and [Harbor](https://github.com/harbor-framework/harbor) runs each task
and its verifier.

```
                 Harbor (host process)
                 ├── parsec_harbor_agent.ParsecAgent ─── POST /api/query (SSE) ──▶ parsec (patched, PARSEC_SIM=1)
                 │        ▲                                                       │  orchestrator._execute_tool
                 │        │ reads the tool-call trace                             │   └─ dispatch_simulated()
                 │        │                                                       ▼
                 │   PARSEC_SIM_TRACE (JSONL) ◀──── one line per call ────── src/parsecsim/sim_backend.py
                 │                                                                 │ MCP over SSE, routed by tool
                 │                                                                 ▼
                 │                     ┌───────────────────── simulation harness, one instance per service ─────────────┐
                 │                     │ platform :8086  github :8087  icinga :8088  cost :8089  cloud :8090             │
                 │                     │ each: bundle (api.json, schema.json, SKILL.md) + store seeded by install_seeds  │
                 │                     └──────────────────────────────────────────────────────────────────────────────┘
                 │
                 └── writes <trial>/agent/agent.jsonl (stream-json transcript)
                                │
                 task container (ubi9): tests/test.sh → tests/verify.py --expected tests/expected.json
                                │
                                ▼
                 <trial>/verifier/reward.json + reward-detail.json
```

## The simulations

The [simulation harness](https://github.com/skillberry-ai/simulation-harness)
(v0.2.0) serves an API as MCP tools and answers every call by prompting a model,
the *simulation model*, with three things: the API's description, the
simulation's instructions, and the contents of a typed in-memory store. The
store is the source of truth, and the model formats a response from what the
store holds.

A **bundle** (`bundles/parsec-<service>/`) is one generated simulation:

| file | role |
|---|---|
| `api.json` | The OpenAPI description of the service: one operation per parsec tool, with its arguments and response shape. Each operation description also states how the store answers it. |
| `schema.json` | The store's schema: its collections, each row's fields, and the primary key. Seed data is validated against this, not against `api.json`. |
| `SKILL.md` | The simulation's instructions. For each operation, it names the collection that operation reads, how it filters, and how it resolves an omitted argument. It also carries the derivation rules and numeric ranges for generated fields. |
| `db.json` | The bundle's own sample data. **No task uses it**: every task installs its own seed, and every undeclared service is emptied. |

The five bundles were generated from hand-written OpenAPI specs of parsec's
tools at commit `28e2c40`. Generation is model-driven and not reproducible, so
the generated bundles themselves are the artifact, and these are the exact
bundles the baseline measured.

**One service per harness process.** A harness process hosts at most one
simulation, so each service runs in its own instance on its own port. The
grouping follows join keys: `platform` holds the four tools that share a
deployment's GUID (AAP2 jobs, Splunk logs, OCPV VMs, Babylon catalog entries),
so one seed can describe one deployment consistently across all four.

| service | tools |
|---|---|
| platform | `query_aap2`, `query_splunk`, `query_ocpv_cluster`, `query_babylon_catalog` |
| github | `fetch_github_file`, `lookup_catalog_item`, `search_github_repo`, `search_agnosticv_prs` |
| icinga | `query_icinga` |
| cost | `query_aws_costs`, `query_gcp_costs`, `query_azure_costs`, `query_aws_capacity_manager`, `query_cost_monitor` |
| cloud | `query_azure_pools`, `query_gcp_projects`, `query_cloudtrail`, `query_aws_account`, `query_aws_account_db`, `query_marketplace_agreements` |

Those twenty tools are the modelled surface. parsec has a few more:
`query_provisions_db` and the `db_*` reporting-database tools, `query_aws_pricing`,
`render_chart`, `generate_report` and `search_github_code`. These are deliberately
out of scope. A call to one returns an in-band error saying the tool is not
modelled, and a task that would have needed one gives the agent the identifier
instead.

**Per-task worlds.** Before each task, `scripts/install_seeds.py` writes the task's
`seeds/<service>.json` into each declared service, through
`PUT /api/v1/simulation/database`. It then reads the data back from both the file
and the live store, and refuses unless both match exactly. Every other live
service gets an empty store, because parsec may call any of its tools whatever
the task. A seed holds the records the question is about, plus deliberate decoys:
a same-named entity on another cluster, a healthy sibling, an older run. Decoys
are what make a wrong-record answer visible.

## The parsec redirect

`patch/parsec-simulation-redirect.patch` applies to parsec `28e2c40` and makes three
changes.

1. **A hook at the top of `orchestrator._execute_tool`.** This is parsec's single
   dispatch point: its MCP server reflects all of its tool schemas onto this one
   function. With `PARSEC_SIM` set, the hook hands every call to
   `dispatch_simulated` before any real backend is reached, including the `db_*`
   branch that would otherwise run first. Everything above the hook is real
   parsec: its routing to sub-agents, prompts, skills and model loop. **Tool
   names stay bare** (`query_aap2`, not `mcp__parsec__query_aap2`), because the
   hook sits below the namespacing the Claude Agent SDK applies, and the
   verifiers match names literally.
2. **`src/parsecsim/`**, the redirect itself. `routing.py` maps each of the
   twenty tools to its service and port, and lists the unmodelled tools.
   `sim_backend.py` makes one MCP call to the right harness and returns parsec's
   own result shape: a dict, with failure as `{"error": ...}` exactly as parsec's
   real tools signal it. It never raises, so the model sees a tool failure it can
   react to rather than a transport fault. Each call is bounded by
   `PARSEC_SIM_TIMEOUT`. Each call and its result is appended as one JSON line to
   `PARSEC_SIM_TRACE`.
3. **Backend gates forced open in `agent/tool_definitions.py`.** parsec hides a
   tool whose real backend is unconfigured, for example `query_icinga` without an
   Icinga URL. Under simulation that would only remove a tool a task needs, and
   the agent would be measured reacting to a missing tool. With `PARSEC_SIM`
   set, the gates are on, and startup **refuses** (`RoutedToolsMissing`) if any
   routed tool would still be hidden. The check runs at import, because a tool
   the model is never shown produces no call for the hook to intercept.

## The Harbor agent

`scripts/parsec_harbor_agent.py`'s `ParsecAgent` is the `--agent` Harbor loads. It runs on the
host, inside Harbor's process, not in the task container. Per task, it:

1. truncates the trace file, so no earlier run's calls leak into this one;
2. sends the task's `instruction.md` to parsec as `POST /api/query` and reads the
   Server-Sent Events stream. Only `event: text` frames form the answer, because
   status and tool-progress frames would fold harness chatter into the graded
   text;
3. joins the answer with the tool calls in the trace, and writes the transcript
   the verifier reads, `<trial>/agent/agent.jsonl`. Each call is an
   `assistant`/`tool_use` event followed by a `user`/`tool_result` event (with
   `is_error` set from the result), and the run ends with exactly one terminal
   `result` event that carries the answer.

Tool calls come from the redirect's trace, not from parsec's MLflow spans: the
trace records bare names and already flags a failed call. `run()` never raises
(except for cancellation, which writes its terminal event first), so a failed run
still reaches the verifier and scores 0, rather than leaving Harbor with no
reward file.

## The task and its contract

A task directory is a standard Harbor task. `task.toml` declares the services
(`[metadata] services`), the tranche and kind, the `ubi9` verifier image, one MCP
server URL template per service, and the timeouts (900 s agent, 120 s verifier).

`tests/expected.json` is the contract:

- **`tool_calls`**: the expected calls, each with the arguments that matter.
  The arguments are matched as a subset, so an incidental `max_results` does not
  break a correct call, and `absent_args` can require an argument's absence when
  the wrong move is an omission. Matching is `ordered-subsequence` (longest
  ordered match) for a dependency chain, `unordered-subset` for sibling calls, or
  `exact-sequence`. **Forbidden calls**, such as a fetch from the wrong
  repository owner, zero the component outright.
- **`answer`**: one denominator over four kinds of item.
  - *Required facts* each accept any of a set of forms. Every one quotes, in
    `asked_by`, the instruction text that asks for it, so a task never grades
    something nobody asked.
  - *Counts* match a number near its noun, in digits or words.
  - *Citations* match a repository and a path.
  - *Forbidden facts* are scored as a point when absent. They are
    polarity-aware, so a correct denial ("not a transient failure",
    "In Downtime: No", a table cell marked false) is not a violation, and
    `attributed_to` excuses a form the answer is quoting or refuting.
- **`weights`**: the split between the two components. It is chosen per task,
  from what the call sequence actually achieves. A call whose arguments are all
  handed over by the instruction earns little weight, and a genuine discovery
  chain earns more.

`tests/verify.py` is the scorer, identical in all 200 tasks. It parses the
transcript, applies the completion gate, scores both components, and writes the
four scalars Harbor reads (`reward.json`), plus `reward-detail.json` naming each
missed fact, hit trap and unmatched call. Harbor runs it in the task container
through `tests/test.sh`. Because the reward is a pure function of the transcript
and the contract, any stored transcript can be re-scored offline:

```bash
python3 tasks/<id>/tests/verify.py --expected tasks/<id>/tests/expected.json \
    --agent-logs <copy-of>/baseline/<id>/agent --out /tmp/out
```

Point `--agent-logs` at a copy, since the verifier writes beside its input.

`golden.json` is an authored reference solution: the calls a correct agent
makes, the results the seed implies, and an answer. It scores 1.0 by
construction.

## How the tasks were made trustworthy

The project's rule was that a wrong measurement is worse than a missing one.
Each task passed the following gates before it was measured:

- **Expected outputs derive from the authored seed, never from any agent's
  output.** Every literal in a task is either attested in parsec's source at
  `28e2c40` or declared as invented in its `provenance.md`.
- **A static gate.** The golden path scores 1.0. The seed validates against the
  bundle's `schema.json`, with no duplicate primary keys. The golden call
  arguments validate against `api.json`. Every required literal is present in the
  seed, and no forbidden literal is (it would defuse its own trap). Every graded
  fact is asked for by the instruction. The instruction uses no wall-clock
  relative language ("yesterday"), because seeds carry absolute timestamps.
- **Discrimination floors.** Three probe agents are scored through each task's
  own verifier, with caps the task must stay under:
  - *mute* makes the golden calls and answers with a fixed content-free sentence
    (at most 0.50);
  - *nocall* makes no calls and gives the same answer (at most 0.25);
  - *fabricate* makes the golden calls and confidently asserts each of the
    contract's forbidden claims (at most 0.35, and no higher than *mute*; a task
    with no forbidden fact has no fabricate floor).

  A task that pays a lazy or fabricating agent more than that is rejected, or
  documents its exemption in `provenance.md`.
- **Hand-scored adversarial answers.** Each contract was checked against honest
  answers phrased unlike the golden (negations, tables, digits or words), which
  must score 1.0. It was also checked against fabricators and decoy readings,
  which must score no higher than *mute*. Where an answer mixing a true literal
  with a false claim still earns partial credit, `provenance.md` records the
  measured residual.
- **Live replay.** Each task's golden calls were replayed against the running
  simulations and compared leaf by leaf with the authored results, and lookups
  on identifiers no seed holds had to come back empty.

## Limits

- **The simulation is a model.** The same task on the same bundles can score
  differently between runs. Read one reward as one sample.
- **The replay checks the golden path only.** An agent's arguments differ, and
  the simulation is less tested off that path. The divergences we know of are
  listed in [`BASELINE.md`](BASELINE.md).
- **The measured agent is parsec, routing included.** When parsec routes a
  question to a sub-agent whose tool set lacks the expected tool, the score
  measures that routing decision. Such rows are labelled.
- **The task mix is not a workload sample.** The tasks were chosen to exercise
  every modelled tool and a range of failure shapes, not in proportion to real
  PARSEC traffic.
