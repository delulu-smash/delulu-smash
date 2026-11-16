from __future__ import annotations

import asyncio
import datetime as dt
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Annotated

import ds.data.paths
import polars as pl
import typer
from ds.cli.util import run_cmd
from ds.data.char_icons import CHAR_ICON_DIR
from ds.data.raw import char_ranking
from ds.data.raw.framedata import scrape_framedata
from ds.data.raw.roster import CHARS_MODULE, scrape_character_roster, with_char_icon, write_char_enums
from ds.data.raw.smashmate import SITE_CHAR_ICON, scrape_char_icons
from ds.data.raw.startgg import videogame_characters, write_startgg_characters

# TODO: consider consolidating to one command for syncing raw
# (ie temp and converting), so can do by file type or entire data

__all__ = ["data_app"]

data_app = typer.Typer(help="SubCommands for raw & transformed data (eg frame data)")

# pkgs/ds/data/ (icons, raw/) and its smash_db/parquet/ folder: SmashDb, one file per table
DATA_DIR = ds.data.paths.DATA_DIR
PARQUET_DIR = ds.data.paths.PARQUET_DIR
# the "database" of characters (id, name, char_icon) synced from ultimateframedata.com
CHAR_PARQUET_PATH = PARQUET_DIR / "char.parquet"
# the "database" of move frame data synced from ultimateframedata.com
FRAMEDATA_PARQUET_PATH = PARQUET_DIR / "framedata.parquet"


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
    """List every SmashDb table (data/smash_db/parquet/): row count, file size, and schema"""
    rows = []
    schemas = {}
    for parquet_path in sorted(PARQUET_DIR.glob("*.parquet")):
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
    """Scrape ultimateframedata.com move frame data and sync it into the framedata table."""
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
    """Fetch start.gg's Ultimate characters (one request) into raw/startgg/characters.py."""
    characters = asyncio.run(videogame_characters())
    df = pl.DataFrame(
        [{"startgg_id": c.id, "name": c.name, "char_group": c.char_group} for c in characters.values()]
    ).sort("startgg_id")
    print(df)
    unmapped = df.filter(pl.col("char_group").is_null())["name"].to_list()
    print(f"No char_group (expected: only 'Random Character'): {unmapped}")
    if typer.confirm(f"Write these {df.height} characters into the start.gg code?"):
        changed = write_startgg_characters(characters)
        print("Updated STARTGG_CHARACTER_NAMES" if changed else "Already up to date")
    else:
        print("Skipped write.")


@data_app.command("roster")
def roster() -> None:
    """Scrape ultimateframedata.com/smash and sync the full roster into the char table."""
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


@data_app.command("char_enum")
def char_enum() -> None:
    """Regenerate the CharId / CharGroup enums (ds/data/chars.py) from the char table."""
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


# the per-character rankings table, loaded from hand-downloaded CSVs (ds.data.raw.char_ranking)
CHAR_RANKING_PARQUET_PATH = PARQUET_DIR / "char_ranking.parquet"


def _char_ranking_steps() -> list[str]:
    """What to do by hand to get a release's zip into the downloads folder. The one list of
    steps: the command's --help, its start and its "no zip" error all print it.
    """
    return [
        "Open the SchuStats Discord and find the Google Drive link posted there (Patreon channels).",
        "In the Drive folder, open 'Character Rankings' and find the month's folder (eg 'November 2026').",
        f"Download that month's folder (right-click > Download): Drive zips it into {char_ranking.DOWNLOADS_DIR}.",
        "Run `ds data char_ranking` (it picks the newest zip there).",
    ]


def _print_char_ranking_steps() -> None:
    print("How to get the file:")
    for step, line in enumerate(_char_ranking_steps(), 1):
        print(f"  {step}. {line}")


# blank lines between the parts: Typer joins the lines of one paragraph
_CHAR_RANKING_HELP = "\n\n".join(
    [
        "Load a month's per-character rankings (a zip of CSVs downloaded by hand) into the table.",
        "How to get the file:",
        *[f"{step}. {line}" for step, line in enumerate(_char_ranking_steps(), 1)],
        "The zip is read in place and you are asked before anything is written.",
    ]
)


# rows of a loaded release to show before writing it
_SAMPLE_ROWS = 10


@data_app.command("char_ranking", help=_CHAR_RANKING_HELP)
def char_ranking_cmd(
    zip_name: Annotated[
        str | None,
        typer.Argument(
            help="The downloaded zip: a file name in ~/Downloads or a path. Default: the newest .zip there."
        ),
    ] = None,
) -> None:
    """Load a month's per-character rankings (a zip of CSVs downloaded by hand) into the table.
    (--help shows _CHAR_RANKING_HELP instead: this text plus how to get the file.)

    Reads the zip in place (nothing is unpacked), works out its month from the folder inside
    (eg 'November 2026' -> 2026-11-30) and asks before loading it into
    data/smash_db/parquet/char_ranking.parquet. Loading a month again replaces only that
    month's rows.
    """
    _print_char_ranking_steps()
    try:
        zip_path = char_ranking.find_zip(zip_name)
        folder, release = char_ranking.release_month(zip_path)
    except (FileNotFoundError, ValueError, zipfile.BadZipFile) as error:
        print(f"Can't load a release: {error} (see the steps above)")
        raise typer.Exit(1) from None
    downloaded = dt.datetime.fromtimestamp(zip_path.stat().st_mtime, tz=dt.UTC).astimezone()
    print(f"Zip: {zip_path} (downloaded {downloaded:%Y-%m-%d %H:%M})")
    typer.confirm(f"Load {folder!r} as the release of {release} (month end)?", default=True, abort=True)

    try:
        df = char_ranking.read_release(zip_path)
    except ValueError as error:  # the format changed, or a ranking's name matches no character
        print(error)
        raise typer.Exit(1) from None
    print(f"{df['char_group_id'].n_unique()} characters -> {df.height} rows; {_SAMPLE_ROWS} of them, by tag:")
    # sorted by tag, so the sample mixes characters and ranks; every column, none cut off
    with pl.Config(tbl_cols=-1, tbl_rows=_SAMPLE_ROWS, tbl_width_chars=200, fmt_str_lengths=40):
        print(df.sort("tag", maintain_order=True).head(_SAMPLE_ROWS))
    table = pl.read_parquet(CHAR_RANKING_PARQUET_PATH) if CHAR_RANKING_PARQUET_PATH.exists() else None
    replaced = 0 if table is None else table.filter(pl.col("date") == release).height
    question = f"Write {df.height} rows for {release} to {CHAR_RANKING_PARQUET_PATH}"
    if not typer.confirm(f"{question}{f' (replacing its {replaced})' if replaced else ''}?", default=True):
        print("Skipped.")
        return
    merged = char_ranking.merge_release(table, df)
    merged.write_parquet(CHAR_RANKING_PARQUET_PATH)
    print(f"Wrote {CHAR_RANKING_PARQUET_PATH}: {merged.height} rows, {merged['date'].n_unique()} releases")


# Data updates (data/ tables) that need a hand step (eg a download), run in order by
# `manual_maintenance`: (what it is, the `ds` command). Data only: other maintenance (packages,
# tech debt) doesn't belong here. The monthly reminder issue
# (.github/workflows/manual_data_maintenance_reminder.yml) only names `manual_maintenance`.
_MANUAL_STEPS = [
    ("Monthly per-character rankings (the month's zip in ~/Downloads)", ["data", "char_ranking"]),
]


@data_app.command("manual_maintenance")
def manual_maintenance() -> None:
    """Run every data-table update that needs a hand step, one after another (monthly reminder)

    Each runs as its own `ds` command, with its own prompts; one that stops or is skipped
    doesn't stop the rest.
    """
    ds = str(Path(sys.executable).parent / "ds")  # this venv's ds, with or without the shell alias
    for number, (what, args) in enumerate(_MANUAL_STEPS, 1):
        print(f"\n[{number}/{len(_MANUAL_STEPS)}] {what}", flush=True)  # before the step's own output
        try:
            run_cmd([ds, *args])
        except subprocess.CalledProcessError:
            print(f"Stopped or skipped: run `ds {' '.join(args)}` on its own later.")
