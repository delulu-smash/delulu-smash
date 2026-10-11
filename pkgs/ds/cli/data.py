from __future__ import annotations

from pathlib import Path

import polars as pl
import typer
from ds.data.raw.framedata import scrape_framedata
from ds.data.raw.roster import scrape_character_roster

# TODO: consider consolidating to one command for syncing raw
# (ie temp and converting), so can do by file type or entire data

__all__ = ["data_app"]

data_app = typer.Typer(help="SubCommands for raw & transformed data (eg frame data)")

# the folder holding our "database" parquet files (each direct child *.parquet is a table)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
# the "database" of characters (id, name, framedata_url) synced from ultimateframedata.com
CHAR_PARQUET_PATH = DATA_DIR / "char.parquet"
# the "database" of move frame data synced from ultimateframedata.com
FRAMEDATA_PARQUET_PATH = DATA_DIR / "framedata.parquet"


BYTES_PER_KB = 1024


def _human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < BYTES_PER_KB:
            return f"{size:.0f}{unit}" if unit == "B" else f"{size:.1f}{unit}"
        size /= BYTES_PER_KB
    return f"{size:.1f}TB"


@data_app.command("summary")
def summary() -> None:
    """List every parquet table in data/ with its row count, file size, and schema"""
    rows = []
    schemas = {}
    for parquet_path in sorted(DATA_DIR.glob("*.parquet")):
        lf = pl.scan_parquet(parquet_path)
        rows.append(
            {
                "table": parquet_path.name,
                # parquet stores row counts in its metadata, so this is a cheap read
                "rows": lf.select(pl.len()).collect().item(),
                "size": _human_size(parquet_path.stat().st_size),
            }
        )
        schemas[parquet_path.name] = lf.collect_schema()
    print(pl.DataFrame(rows))
    for table, schema in schemas.items():
        print(f"\n{table} schema:")
        with pl.Config(tbl_rows=-1):
            dtypes = [str(dtype) for dtype in schema.dtypes()]
            print(pl.DataFrame({"column": schema.names(), "dtype": dtypes}))


@data_app.command("framedata")
def framedata(
    character: str | None = typer.Argument(
        None,
        help="Character slug from the ultimateframedata.com URL (eg little_mac). Omit for all.",
    ),
) -> None:
    """Scrape ultimateframedata.com move frame data and sync into data/framedata.parquet."""
    if character is not None:
        df = scrape_framedata(character)
    else:
        characters = pl.read_parquet(CHAR_PARQUET_PATH)["id"].to_list()
        df = pl.concat([scrape_framedata(c) for c in characters], how="diagonal_relaxed")
    print(df)
    if typer.confirm(f"Overwrite {FRAMEDATA_PARQUET_PATH} with these {df.height} moves?"):
        df.write_parquet(FRAMEDATA_PARQUET_PATH)
        print(f"Wrote {df.height} moves to {FRAMEDATA_PARQUET_PATH}")
    else:
        print("Skipped write.")


@data_app.command("roster")
def roster() -> None:
    """Scrape ultimateframedata.com/smash and sync the full roster into data/char.parquet."""
    df = scrape_character_roster()
    print(df)
    if typer.confirm(f"Overwrite {CHAR_PARQUET_PATH} with these {df.height} characters?"):
        df.write_parquet(CHAR_PARQUET_PATH)
        print(f"Wrote {df.height} characters to {CHAR_PARQUET_PATH}")
    else:
        print("Skipped write.")
