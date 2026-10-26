#!/usr/bin/env python3
"""Install one task's seed data into the running simulations.

Self-contained: standard library only, no imports from the benchmark repository.

    python3 scripts/install_seeds.py tasks/bench-v4-platform-002-collection-not-found-rca
    python3 scripts/install_seeds.py --bundles DIR tasks/bench-v4-...   # zips elsewhere

A task declares its services in task.toml (`[metadata] services = [...]`) and
carries one seeds/<service>.json per declared service. One harness instance hosts
one service, so each seed goes to a different port.

Two rules are enforced here rather than left to memory:

  * Every declared service must have a seed file. A service that is reachable but
    unseeded serves whatever the previous task left behind, which produces a
    plausible reward for the wrong dataset.
  * Every seed file must belong to a declared service. An orphan is an unfinished
    task.toml edit that would otherwise be silently ignored.

Every service the task does NOT declare, but which has a live simulation, is
installed EMPTY: every collection of its bundle's schema.json, as []. The schema
is read from parsec-<service>-skill-bundle.zip or, failing that, from an
unpacked parsec-<service>/schema.json -- in the bundles directory: beside this
script, else a bundles/ beside it or beside its parent, unless --bundles names one.
parsec calls every tool it has whether or not the task
declares that service, so an undeclared live service would otherwise answer from
the previous task's seed. It is not reset to the bundle's db.json, which is
generated sample data no task authored: a call reaching it would read those rows
as the task's world. An idle or unreachable service is left alone; one still
starting is refused.

Every PUT is read back twice, from two endpoints that answer different
questions, and each must equal what was PUT exactly or the install is refused:

  * /api/v1/simulation/database serves db.json from disk. It proves the file
    landed.
  * /api/v1/simulation/state serves the simulator's in-memory store. It proves
    the simulation can actually read what was seeded.

The second is the one that matters. The store keys rows by str(primary key) and
keeps only the last row with a given key, so a seed with two rows sharing a key
round-trips through the file perfectly while the store holds fewer rows than the
seed declares. The tool calls would then be answered from data nobody authored,
and the difference is invisible in a reward. On a store mismatch the error lists,
per collection, how many rows were seeded and how many the store holds.

An unreachable port is refused for a declared service ("cannot reach ...") and
skipped for an undeclared one, which cannot serve anything.
"""

from __future__ import annotations

import json
import sys
import tomllib
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

#: Published port per service. Must match the harness topology you brought up.
SERVICE_PORTS: dict[str, int] = {
    "platform": 8086,
    "github": 8087,
    "icinga": 8088,
    "cost": 8089,
    "cloud": 8090,
}

SIMULATION_PATH = "/api/v1/simulation"
DATABASE_PATH = f"{SIMULATION_PATH}/database"
STATE_PATH = f"{SIMULATION_PATH}/state"
HOST = "http://localhost"
_HERE = Path(__file__).resolve().parent
#: Beside this script (the zipped handover layout), else bundles/ beside it or
#: beside its parent (the flat layout, where this script lives in scripts/).
BUNDLES_DIR = next(
    (d for d in (_HERE / "bundles", _HERE.parent / "bundles") if d.is_dir()), _HERE
) if not any(_HERE.glob("parsec-*-skill-bundle.zip")) else _HERE


class SeedError(Exception):
    """The task's seeds are unusable, or the harness did not accept them."""


def _request(method: str, url: str, body: bytes | None) -> tuple[int, bytes]:
    request = urllib.request.Request(
        url, data=body, method=method,
        headers={"content-type": "application/json"})
    try:
        with urllib.request.urlopen(request) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()
    except urllib.error.URLError as exc:
        raise SeedError(f"cannot reach {url}: {exc.reason}. Is the harness up?") from exc


def services_of(task_dir: Path) -> list[str]:
    toml_path = task_dir / "task.toml"
    if not toml_path.exists():
        raise SeedError(f"no task.toml in {task_dir}")
    meta = tomllib.loads(toml_path.read_text()).get("metadata") or {}
    services = meta.get("services")
    if not services:
        raise SeedError(
            f"{toml_path} declares no [metadata] services. A bench-v4 task must "
            f"list every service it needs.")
    unknown = [s for s in services if s not in SERVICE_PORTS]
    if unknown:
        raise SeedError(f"unknown service(s) {unknown}; known: {sorted(SERVICE_PORTS)}")
    return list(services)


def _put_and_verify(service: str, seed: dict) -> None:
    url = f"{HOST}:{SERVICE_PORTS[service]}{DATABASE_PATH}"

    status, response = _request("PUT", url, json.dumps(seed).encode())
    if not 200 <= status < 300:
        raise SeedError(
            f"{service}: seed install returned HTTP {status}: "
            f"{response.decode(errors='replace')[:400]}\n"
            f"Refusing to run. 422 means the seed does not satisfy that "
            f"bundle's schema.json; 409 means tool calls are still in flight; "
            f"404 usually means no simulation is active on that port.")

    status, served = _request("GET", url, None)
    if not 200 <= status < 300:
        raise SeedError(f"{service}: could not read the database back (HTTP {status})")
    if json.loads(served) != seed:
        raise SeedError(
            f"{service}: the PUT succeeded but {url} serves different data. "
            f"Refusing to run -- the reward would describe the wrong dataset.")

    state_url = f"{HOST}:{SERVICE_PORTS[service]}{STATE_PATH}"
    status, snapshot = _request("GET", state_url, None)
    if not 200 <= status < 300:
        raise SeedError(
            f"{service}: could not read the store back from {state_url} "
            f"(HTTP {status})")
    snapshot = json.loads(snapshot)
    if snapshot != seed:
        raise SeedError(
            f"{service}: the file round-trips but the STORE on {state_url} does "
            f"not hold the seed.\n{_store_diff(seed, snapshot)}\n"
            f"Refusing to run -- the tool calls would be answered from data "
            f"nobody authored. The usual cause is two rows in one collection "
            f"sharing a primary key: the store keeps only the last row per key.")


def _store_diff(seed: dict, snapshot: dict) -> str:
    """Per-collection row counts, seed vs store, for the collections that differ."""
    lines = []
    for collection in sorted(set(seed) | set(snapshot)):
        want, got = seed.get(collection), snapshot.get(collection)
        if want == got:
            continue
        if isinstance(want, list) and isinstance(got, list):
            lines.append(f"  {collection}: seeded {len(want)} rows, store has {len(got)}")
        elif collection not in snapshot:
            lines.append(f"  {collection}: seeded but absent from the store")
        elif collection not in seed:
            lines.append(f"  {collection}: in the store but not in the seed")
        else:
            lines.append(f"  {collection}: contents differ")
    return "\n".join(lines) or "  (no per-collection difference; contents differ)"


def _is_live(service: str) -> bool:
    """True if a ready simulation is on the service's port; raise if one is starting."""
    url = f"{HOST}:{SERVICE_PORTS[service]}{SIMULATION_PATH}"
    try:
        status, body = _request("GET", url, None)
    except SeedError:
        return False  # unreachable: nothing can be served
    if status == 404:
        return False
    try:
        sim_status = json.loads(body).get("status") if status == 200 else None
    except (ValueError, AttributeError):
        sim_status = None
    if sim_status == "failed":
        return False
    if sim_status != "ready":
        raise SeedError(
            f"{service}: not declared by this task, but its simulation is "
            f"{sim_status or f'HTTP {status}'}, not ready, so it cannot be "
            f"installed empty. Wait for it to be ready, or tear it down.")
    return True


def empty_store(service: str, bundles_dir: Path) -> dict:
    """Every collection of the bundle's schema.json, holding no rows.

    Read from the shipped bundle (parsec-<service>-skill-bundle.zip, or the
    unpacked parsec-<service>/ directory) rather than from the harness's skills
    directory, so a stray edit there cannot change what "empty" means.
    """
    zip_path = Path(bundles_dir) / f"parsec-{service}-skill-bundle.zip"
    dir_path = Path(bundles_dir) / f"parsec-{service}" / "schema.json"
    source = zip_path if zip_path.is_file() or not dir_path.is_file() else dir_path
    try:
        if source == zip_path:
            with zipfile.ZipFile(zip_path) as bundle:
                schema = json.loads(bundle.read(f"parsec-{service}/schema.json"))
        else:
            schema = json.loads(dir_path.read_text())
    except (OSError, KeyError, ValueError, zipfile.BadZipFile) as exc:
        raise SeedError(
            f"{service}: live but not declared by this task, and its bundle schema "
            f"could not be read from {source} ({exc}). Refusing to run against "
            f"whatever it already holds; pass --bundles DIR.") from exc
    collections = schema.get("properties") or {}
    if not collections:
        raise SeedError(f"{service}: {source}'s schema.json declares no collections")
    return {name: [] for name in collections}


def install(task_dir: Path, bundles_dir: Path = BUNDLES_DIR) -> None:
    task_dir = Path(task_dir)
    declared = services_of(task_dir)
    seeds_dir = task_dir / "seeds"

    present = {p.stem for p in sorted(seeds_dir.glob("*.json"))}
    missing = [s for s in declared if s not in present]
    if missing:
        raise SeedError(
            f"{task_dir.name} declares {declared} but has no seed for {missing}. "
            f"Refusing: an unseeded service serves the previous task's data.")
    orphans = sorted(present - set(declared))
    if orphans:
        raise SeedError(
            f"{task_dir.name} has seeds/{orphans} for services it does not "
            f"declare. Refusing: an orphan seed is silently ignored at run time.")

    # Every reset is resolved before anything is written, so a refusal leaves
    # no half-installed task behind.
    resets = {s: empty_store(s, bundles_dir)
              for s in SERVICE_PORTS if s not in declared and _is_live(s)}

    for service in declared:
        _put_and_verify(service, json.loads((seeds_dir / f"{service}.json").read_text()))
        print(f"  {service}: seeded and verified on port {SERVICE_PORTS[service]}")
    for service, seed in resets.items():
        _put_and_verify(service, seed)
        print(f"  {service}: not declared; installed empty on port "
              f"{SERVICE_PORTS[service]}")


def main(argv: list[str]) -> int:
    args = argv[1:]
    bundles_dir = BUNDLES_DIR
    if len(args) == 3 and args[0] == "--bundles":
        bundles_dir, args = Path(args[1]), args[2:]
    if len(args) != 1:
        print(__doc__)
        return 2
    try:
        install(Path(args[0]), bundles_dir)
    except SeedError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
