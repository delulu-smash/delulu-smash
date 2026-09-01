from __future__ import annotations

import typer
from ds import SETTINGS
from ds.settings import set_settings

__all__ = ["settings_app"]

settings_app = typer.Typer(help="SubCommands for syncing up settings")


@settings_app.command("sync")
def sync() -> None:
    """Sync settings (eg OpenAI API key)"""
    openai_api_key = typer.prompt("Enter your OpenAI API key (eg sk-xxxx)", hide_input=True)
    set_settings(openai_api_key=openai_api_key)
    print(f"Current Settings: {SETTINGS}")


@settings_app.command("show")
def show() -> None:
    """Display current settings"""
    print(SETTINGS)
