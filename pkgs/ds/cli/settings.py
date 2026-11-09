from __future__ import annotations

import typer
from ds.settings import get_settings, set_settings

__all__ = ["settings_app"]

settings_app = typer.Typer(help="SubCommands for syncing up settings")


@settings_app.command("sync")
def sync() -> None:
    """Sync settings (Pydantic AI Gateway key) into keyring"""
    # from Logfire Gateway > Connect; used by all ds.ai model calls (DEFAULT_AI_MODEL)
    pydantic_gateway_api_key = typer.prompt("Enter your Pydantic AI Gateway key (eg pylf_v1_us_xxxx)", hide_input=True)
    set_settings(pydantic_gateway_api_key=pydantic_gateway_api_key)
    print(f"Current Settings: {get_settings()}")


@settings_app.command("show")
def show() -> None:
    """Display current settings"""
    print(get_settings())
