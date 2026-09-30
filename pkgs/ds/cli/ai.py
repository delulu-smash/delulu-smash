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


@ai_app.command("eval")
def eval_(
    name_filter: str = typer.Argument("", help="Only run cases whose name contains this, eg 'stale'"),
) -> None:
    """Run the Smash knowledge evals (ds/ai/evals/smash_knowledge.yaml) against the ai agent.

    Calls the OpenAI API (agent + LLM judge), so each run costs a little.
    """
    from ds.ai.evals import run_knowledge_evals

    report = run_knowledge_evals(name_filter)
    report.print(include_input=True, include_output=True, include_reasons=True)
