"""entry point for our `ds` cli app (as specified in pyproject.toml [project.scripts])"""

from __future__ import annotations

from util.cli.core import app
from util.cli.docs import docs_app
from util.cli.ui import ui_app

app.add_typer(docs_app, name="docs")
app.add_typer(ui_app, name="ui")
