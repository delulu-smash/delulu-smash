from __future__ import annotations

import typer
from ds.cli.util import run_cmd
from ds.util.const import REPO_DIR

__all__ = ["ui_app"]


ui_app = typer.Typer(help="SubCommands for reflex ui tool")

TOOLS_DIR = REPO_DIR / "tools" / "smash"


@ui_app.command("run")
def run() -> None:
    """Run reflex ui server"""
    run_cmd(["uv", "run", f"--directory={TOOLS_DIR}", "reflex", "run"])
