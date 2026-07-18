"""entry point for our `ds` cli app (as specified in pyproject.toml [project.scripts])"""

# TODO: creating CLI command that can easily take single vod
# list of time stamps and ability to create gif snippets, with option to load to R2
from __future__ import annotations

import typer
from ds.cli.docs import docs_app
from ds.cli.publish import publish_cmd
from ds.cli.ui import ui_app

app = typer.Typer(
    # some locals contains user passwrods so want ensure dont
    # to CLI
    # pretty_exceptions_enable=False
)
app.command(name="publish")(publish_cmd)


app.add_typer(docs_app, name="docs")
app.add_typer(ui_app, name="ui")
