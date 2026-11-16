from __future__ import annotations

import asyncio
from pathlib import Path

import polars as pl
import typer
from ds.data.char_icons import CHAR_ICON_DIR
from ds.data.raw.framedata import scrape_framedata
from ds.data.raw.roster import CHARS_MODULE, scrape_character_roster, with_char_icon, write_char_enums
from ds.data.raw.smashmate import SITE_CHAR_ICON, scrape_char_icons
from ds.data.raw.startgg import videogame_characters
from ds.data.startgg.characters import STARTGG_CHAR_PARQUET, characters_table

# TODO: consider consolidating to one command for syncing raw
# (ie temp and converting), so can do by file type or entire data

__all__ = ["data_app"]

data_app = typer.Typer(help="SubCommands for raw & transformed data (eg frame data)")

# the folder holding our "database" parquet files (each direct child *.parquet is a table)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
# the "database" of characters (id, name, char_icon) synced from ultimateframedata.com
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


@data_app.command("startgg-char")
def startgg_char() -> None:
    """Fetch start.gg's Ultimate characters (one request) into data/startgg_char.parquet."""
    characters = asyncio.run(videogame_characters())
    df = characters_table(characters)
    print(df)
    unmapped = df.filter(pl.col("char_group").is_null())["name"].to_list()
    print(f"No char_group (expected: only 'Random Character'): {unmapped}")
    if typer.confirm(f"Overwrite {STARTGG_CHAR_PARQUET} with these {df.height} characters?"):
        df.write_parquet(STARTGG_CHAR_PARQUET)
        print(f"Wrote {df.height} characters to {STARTGG_CHAR_PARQUET}")
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
        _sync_char_enums(df)
    else:
        print("Skipped write.")


def _sync_char_enums(char_df: pl.DataFrame) -> None:
    changed = write_char_enums(char_df)
    print(f"{'Updated' if changed else 'Already up to date:'} CharId / CharGroup in {CHARS_MODULE}")
    if changed:
        # startgg_char.parquet's char_group column is typed by CharGroup (CHAR_GROUP_DTYPE)
        print("CharGroup may have changed: re-run `uv run ds data startgg-char` too")


@data_app.command("char_enum")
def char_enum() -> None:
    """Regenerate the CharId / CharGroup enums (ds/data/chars.py) from data/char.parquet."""
    _sync_char_enums(pl.read_parquet(CHAR_PARQUET_PATH))


@data_app.command("char_icon")
def char_icon() -> None:
    """Download the character icons from nasmashmate.com; set char.parquet's char_icon."""
    char_df = with_char_icon(pl.read_parquet(CHAR_PARQUET_PATH))
    missing = char_df.filter(pl.col("char_icon").is_null())["id"].to_list()
    if missing:
        print(f"No icon mapped for: {missing} (add them to SITE_CHAR_ICON in ds.data.raw.smashmate)")
    files = char_df["char_icon"].drop_nulls().n_unique()
    print(char_df)
    if not typer.confirm(
        f"Download {files} icons for {len(SITE_CHAR_ICON)} characters into {CHAR_ICON_DIR} (overwrites)?"
    ):
        print("Skipped.")
        return
    with pl.Config(tbl_rows=-1):
        print(scrape_char_icons(CHAR_ICON_DIR))
    char_df.write_parquet(CHAR_PARQUET_PATH)
    print(f"Wrote the icons to {CHAR_ICON_DIR} and the char_icon column to {CHAR_PARQUET_PATH}")
