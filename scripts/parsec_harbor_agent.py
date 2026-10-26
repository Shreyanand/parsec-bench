#!/usr/bin/env python3
"""ParsecAgent -- run a patched parsec as the Harbor agent under test.

Self-contained apart from `harbor` and `httpx`: nothing here is imported from the
benchmark repository. Load it with

    harbor run -a parsec_harbor_agent:ParsecAgent

Preconditions:

  * the five simulations are up, with this task's seeds installed
    (see install_seeds.py);
  * a parsec patched with parsec-simulation-redirect.patch is listening on
    PARSEC_URL (default http://localhost:8000), started with PARSEC_SIM=1 and
    PARSEC_SIM_TRACE pointing at a path THIS process can also read.

How it works. Parsec is driven over its own HTTP surface, `POST /api/query`, which
streams Server-Sent Events. Its tool calls are read from the JSONL trace the
redirect appends to PARSEC_SIM_TRACE -- not from parsec's MLflow spans -- for two
reasons that matter to scoring:

  * the recorded names are **bare** (`query_aap2`), because the redirect
    intercepts inside orchestrator._execute_tool, below the `mcp__parsec__`
    naming the Claude Agent SDK applies. The verifiers match names literally.
  * a content-level failure (`{"error": ...}`) is already flagged by the sink, so
    a failed call is recorded as failed.

Two invariants, both deliberate:

  * `run()` never raises except asyncio.CancelledError, which writes its terminal
    event and *then* re-raises. If run() raises, Harbor can end the trial with no
    reward file at all, which is indistinguishable from a broken pipeline;
    swallowing means the verifier still runs and records a 0.
  * Exactly one terminal `result` event per run. The verifier reads the last one.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any

from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

#: Parsec mounts its routers under /api. A POST to the bare "/query" returns 405.
QUERY_PATH = "/api/query"
DEFAULT_PARSEC_URL = "http://localhost:8000"
TRACE_ENV = "PARSEC_SIM_TRACE"

LOG_FILENAME = "agent.jsonl"


class StreamJsonWriter:
    """Claude-Code-style stream-json, the format Harbor task verifiers read.

    The shape is dictated by each task's tests/verify.py, which scans for
    assistant events carrying `tool_use` content blocks and a terminal `result`
    event. Events are flushed as written, so a timed-out run still leaves a
    partial, parseable transcript.
    """

    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text("", encoding="utf-8")

    def _write(self, event: dict[str, Any]) -> None:
        line = json.dumps(event, default=str, ensure_ascii=False)
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def init(self, tools: list[str]) -> None:
        self._write({"type": "system", "subtype": "init", "tools": list(tools)})

    def assistant_tool_uses(self, calls: list[dict[str, Any]]) -> None:
        self._write({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "id": c["id"], "name": c["name"],
             "input": c["input"]} for c in calls]}})

    def tool_results(self, results: list[dict[str, Any]]) -> None:
        self._write({"type": "user", "message": {"content": [
            {"type": "tool_result", "tool_use_id": r["tool_use_id"],
             "content": r["content"], "is_error": bool(r.get("is_error", False))}
            for r in results]}})

    def result_success(self, answer: str) -> None:
        self._write({"type": "result", "subtype": "success",
                     "is_error": False, "result": answer})

    def result_error(self, message: str) -> None:
        self._write({"type": "result", "subtype": "error_during_execution",
                     "is_error": True, "result": message})


def read_trace(path: Path | str | None) -> list[dict[str, Any]]:
    """Tool calls from the redirect trace; a bad line is skipped, never fatal."""
    if path is None:
        return []
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return []
    calls = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(entry, dict):
            calls.append(entry)
    return calls


class ParsecAgent(BaseAgent):
    SUPPORTS_ATIF = False
    SUPPORTS_RESUME = False
    SUPPORTS_WINDOWS = False

    @staticmethod
    def name() -> str:
        return "parsec"

    def version(self) -> str:
        return "0.1.0"

    async def setup(self, environment: BaseEnvironment) -> None:
        """Nothing to install: parsec runs as its own service and this adapter
        runs host-side in Harbor's process."""
        return None

    # -- run context -------------------------------------------------------

    def _parsec_url(self) -> str:
        return os.environ.get("PARSEC_URL", "").strip() or DEFAULT_PARSEC_URL

    def _trace_path(self) -> Path | None:
        raw = os.environ.get(TRACE_ENV, "").strip()
        return Path(raw) if raw else None

    def _reset_trace(self) -> None:
        """Truncate the trace before the run.

        The sink appends, so without this one task's calls leak into the next
        one's trajectory -- a wrong measurement rather than a loud failure.
        """
        path = self._trace_path()
        if path is None:
            return
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("", encoding="utf-8")
        except OSError:
            self.logger.warning("could not truncate the parsec trace at %s", path)

    # -- driving parsec ----------------------------------------------------

    @staticmethod
    def _answer_from_sse(lines) -> str:
        """Accumulate the answer from an SSE stream.

        Only `event: text` contributes. status, tool_start and tool_result events
        carry a data payload too, and counting them would put harness chatter
        into the graded answer.
        """
        answer: list[str] = []
        event = ""
        for raw in lines:
            line = raw.rstrip("\n")
            if line.startswith("event:"):
                event = line[len("event:"):].strip()
                continue
            if not line.startswith("data:"):
                continue
            try:
                data = json.loads(line[len("data:"):].strip())
            except (json.JSONDecodeError, ValueError):
                continue
            if not isinstance(data, dict):
                continue
            if event == "text":
                answer.append(str(data.get("content", "")))
            elif event == "error":
                raise RuntimeError(str(data.get("message", "parsec reported an error")))
        return "".join(answer)

    async def _ask_parsec(self, question: str) -> str:
        import httpx

        # No client timeout: each simulated tool call takes 30-60s, so a multi-hop
        # trajectory legitimately runs for minutes. Harbor's own agent timeout is
        # the bound, and it arrives as CancelledError.
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST", f"{self._parsec_url()}{QUERY_PATH}",
                json={"question": question},
                headers={"X-Forwarded-Email": os.environ.get(
                    "PARSEC_BENCH_USER", "bench@local")},
            ) as response:
                response.raise_for_status()
                lines = [line async for line in response.aiter_lines()]
        return self._answer_from_sse(lines)

    # -- the run -----------------------------------------------------------

    def _write_trajectory(self, writer: StreamJsonWriter,
                          calls: list[dict[str, Any]]) -> None:
        for index, call in enumerate(calls):
            call_id = f"parsec_{index}"
            writer.assistant_tool_uses([{
                "id": call_id, "name": call.get("name", ""),
                "input": call.get("arguments") or {}}])
            writer.tool_results([{
                "tool_use_id": call_id,
                "content": json.dumps(call.get("result"), default=str),
                "is_error": bool(call.get("is_error", False))}])

    async def run(self, instruction: str, environment: BaseEnvironment,
                  context: AgentContext) -> None:
        try:
            writer = StreamJsonWriter(Path(self.logs_dir) / LOG_FILENAME)
        except OSError as exc:
            self.logger.exception("could not open the agent transcript")
            context.metadata = {
                "error": f"transcript unavailable: {type(exc).__name__}: {exc}"}
            return

        self._reset_trace()

        try:
            answer = await self._ask_parsec(instruction)
        except asyncio.CancelledError as exc:
            # Harbor enforces its agent timeout with asyncio.wait_for, which
            # cancels this coroutine. CancelledError is a BaseException, so the
            # broad handler below never sees it. Write the terminal event so the
            # verifier can still score the run, then re-raise.
            self.logger.warning("parsec agent cancelled (agent timeout)")
            self._write_trajectory(writer, read_trace(self._trace_path()))
            writer.result_error(f"{type(exc).__name__}: agent timed out")
            context.metadata = {"error": "cancelled: agent timed out"}
            raise
        except Exception as exc:  # noqa: BLE001 - see the module docstring
            self.logger.exception("parsec agent failed")
            self._write_trajectory(writer, read_trace(self._trace_path()))
            writer.result_error(f"{type(exc).__name__}: {exc}")
            context.metadata = {"error": f"{type(exc).__name__}: {exc}"}
            return

        calls = read_trace(self._trace_path())
        self._write_trajectory(writer, calls)
        writer.result_success(answer)
        context.metadata = {
            "tool_calls": [c.get("name", "") for c in calls],
            "failed_tool_calls": sum(1 for c in calls if c.get("is_error")),
            "parsec_url": self._parsec_url(),
        }
        self.logger.info("run complete: %d tool call(s)", len(calls))
