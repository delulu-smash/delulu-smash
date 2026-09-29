from __future__ import annotations

import typer
from ds.cli.util import run_cmd
from ds.util.const import REPO_DIR

__all__ = ["ai_app"]

ai_app = typer.Typer(help="SubCommands for running ai bot")


@ai_app.command("run")
def run() -> None:
    """Run ai chat bot"""
    run_cmd(["uv", "run", "textual-kernel"], cwd=REPO_DIR / "experimental" / "textual-kernel")
