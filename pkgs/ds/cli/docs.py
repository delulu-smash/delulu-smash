from __future__ import annotations

import typer
from ds.cli.util import run_cmd
from ds.util.const import REPO_DIR

__all__ = ["docs_app"]

DOCS_DIR = REPO_DIR / "docs"

docs_app = typer.Typer(help="SubCommands for running docs")


@docs_app.command("run")
def run() -> None:
    """Run docs server"""
    run_cmd(["uvx", f"--directory={DOCS_DIR}", "--from=mystmd", "myst", "start"])
