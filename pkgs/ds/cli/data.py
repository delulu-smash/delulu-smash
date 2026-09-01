from __future__ import annotations

from pathlib import Path

import typer
from ds.data.raw.framedata import scrape_framedata

__all__ = ["data_app"]

data_app = typer.Typer(help="SubCommands for raw & transformed data (eg frame data)")


@data_app.command("framedata")
def framedata(
    character: str = typer.Argument(..., help="Character slug (eg little_mac), matches ultimateframedata.com URL"),
    out: Path | None = typer.Option(None, "--out", "-o", help="Write result to this CSV path instead of printing"),
) -> None:
    """Scrape ultimateframedata.com move frame data for a character into a polars DataFrame"""
    df = scrape_framedata(character)
    if out is not None:
        df.write_csv(out)
        print(f"Wrote {df.height} moves to {out}")
    else:
        print(df)
        print(df.schema)
