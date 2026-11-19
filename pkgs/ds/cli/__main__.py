"""entry point for our `ds` cli app (as specified in pyproject.toml [project.scripts])"""

# TODO: creating CLI command that can easily take single vod
# list of time stamps and ability to create gif snippets, with option to load to R2
from __future__ import annotations

import signal

import typer
from ds.cli.ai import ai_app
from ds.cli.data import data_app
from ds.cli.docs import docs_app
from ds.cli.lint import lint_app
from ds.cli.publish import publish_cmd
from ds.cli.settings import settings_app
from ds.cli.test import test_app
from ds.cli.ui import ui_app

# polars (imported by ds.cli.data) installs a native SIGINT handler that restarts blocking
# reads, so Ctrl+C at any prompt (eg `ds settings sync`) did nothing. Interrupting the read
# lets Python raise KeyboardInterrupt; polars' handler stays, so queries still stop on Ctrl+C.
if hasattr(signal, "siginterrupt"):  # Unix only: Windows has no such call (and no such problem)
    signal.siginterrupt(signal.SIGINT, True)  # noqa: FBT003 -- stdlib signature takes no keyword

app = typer.Typer(
    # some locals contains user passwrods so want ensure dont
    # to CLI
    # pretty_exceptions_enable=False  # noqa: ERA001 -- kept as a ready-to-enable option
)
app.command(name="publish")(publish_cmd)

app.add_typer(docs_app, name="docs")
app.add_typer(ui_app, name="ui")
app.add_typer(settings_app, name="settings")
app.add_typer(data_app, name="data")
app.add_typer(ai_app, name="ai")
app.add_typer(lint_app, name="lint")
app.add_typer(test_app, name="test")
