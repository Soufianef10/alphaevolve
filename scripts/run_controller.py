#!/usr/bin/env python
"""Package-local wrapper that forwards to the top-level `scripts/run_controller.py`.

Installing via `pip` exposes the console-script `run-controller` (declared in
pyproject.toml) which calls `pwb_alphaevolve.scripts.run_controller:main`.

If you’re running directly from source, you can still do either:

    python scripts/run_controller.py          # path relative clone root
    python -m pwb_alphaevolve.scripts.run_controller  # package module
"""
from __future__ import annotations
import importlib.resources as pkg_resources
import runpy
from pathlib import Path
import sys


def main():  # noqa: D401 – simple entry point
    # Locate the repository-root version of the script (editable install) and exec
    repo_root_script = (
        Path(__file__).resolve().parents[2] / "scripts" / "run_controller.py"
    )
    if repo_root_script.exists():
        runpy.run_path(repo_root_script.as_posix(), run_name="__main__")
    else:
        # Fallback – maybe we installed via wheel and included a copy here.
        from pwb_alphaevolve.evolution.controller import ProgramStore, Controller  # type: ignore
        import asyncio

        args = sys.argv[1:]
        print("Running bundled controller – args:", args)
        asyncio.run(Controller(ProgramStore()).run_forever())


if __name__ == "__main__":
    main()
