#!/usr/bin/env python3
"""Create GIFs from MP4 snippets using ffmpeg.

Usage examples:
  python scripts/create_gifs.py snippet input.mp4 --start 00:00:10 --end 00:00:15
  python scripts/create_gifs.py snippet input.mp4 --start 12.5 --duration 3.2 -o out.gif

This script requires `ffmpeg` to be installed and available on PATH.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Annotated

import typer

app = typer.Typer(help="Create GIFs from MP4 snippets using ffmpeg")


def parse_time_to_seconds(t: str) -> float:
    """Parse a time string into seconds.

    Accepts formats like "12.5" or "00:01:23" (H:MM:SS or M:SS).
    """
    if ":" in t:
        parts = [float(p) for p in t.split(":")]
        parts = parts[::-1]
        seconds = 0.0
        mul = 1.0
        for p in parts:
            seconds += p * mul
            mul *= 60.0
        return seconds
    return float(t)


@app.command()
def snippet(
    input_file: Annotated[Path, typer.Argument(metavar="INPUT", exists=True, readable=True)],
    start: Annotated[str, typer.Option(help="Start time (seconds or HH:MM:SS)")],
    end: Annotated[str | None, typer.Option(help="End time (seconds or HH:MM:SS)")] = None,
    duration: Annotated[float | None, typer.Option(help="Duration in seconds (alternative to --end)")] = None,
    output: Annotated[Path | None, typer.Option("-o", help="Output gif path")] = None,
    fps: Annotated[int, typer.Option(help="Frames per second for the GIF")] = 15,
    width: Annotated[int, typer.Option(help="Output GIF width in pixels (height auto)")] = 480,
    overwrite: Annotated[bool, typer.Option("--overwrite", "-y", help="Overwrite output if exists")] = False,
) -> None:
    """Create a GIF from a segment of an input MP4 using ffmpeg.

    Provide either `--end` or `--duration`.
    """
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        typer.echo("ffmpeg not found in PATH. Install ffmpeg and try again.", err=True)
        raise typer.Exit(code=1)

    try:
        start_s = parse_time_to_seconds(start)
    except ValueError:
        typer.echo("Invalid --start value", err=True)
        raise typer.Exit(code=2) from None

    if end is None and duration is None:
        typer.echo("Either --end or --duration must be provided.", err=True)
        raise typer.Exit(code=3)

    if duration is None:
        try:
            end_s = parse_time_to_seconds(end)  # type: ignore[arg-type]
        except ValueError:
            typer.echo("Invalid --end value", err=True)
            raise typer.Exit(code=4) from None
        duration_s = end_s - start_s
        if duration_s <= 0:
            typer.echo("--end must be after --start", err=True)
            raise typer.Exit(code=5)
    else:
        duration_s = float(duration)
        if duration_s <= 0:
            typer.echo("--duration must be positive", err=True)
            raise typer.Exit(code=6)

    if output is None:
        output = input_file.with_suffix(".gif")

    if output.exists() and not overwrite:
        typer.echo(f"Output {output} exists. Use --overwrite to replace.", err=True)
        raise typer.Exit(code=7)

    # temp dir (not mktemp) so the palette path can't be raced; removed automatically on exit
    with tempfile.TemporaryDirectory() as tmp_dir:
        palette = Path(tmp_dir) / "palette.png"
        # First pass: generate a palette tuned for the clipped segment
        cmd1 = [
            ffmpeg_path,
            "-ss",
            str(start_s),
            "-t",
            str(duration_s),
            "-i",
            str(input_file),
            "-vf",
            f"fps={fps},scale={width}:-1:flags=lanczos,palettegen",
            "-y",
            str(palette),
        ]

        # Second pass: create the GIF using the generated palette
        cmd2 = [
            ffmpeg_path,
            "-ss",
            str(start_s),
            "-t",
            str(duration_s),
            "-i",
            str(input_file),
            "-i",
            str(palette),
            "-lavfi",
            f"fps={fps},scale={width}:-1:flags=lanczos[x];[x][1:v]paletteuse",
            "-y",
            str(output),
        ]
        try:
            typer.echo("Generating palette...")
            subprocess.run(cmd1, check=True)
            typer.echo("Creating GIF...")
            subprocess.run(cmd2, check=True)
        except subprocess.CalledProcessError as e:
            typer.echo(f"ffmpeg failed: {e}", err=True)
            raise typer.Exit(code=8) from None

    typer.secho(f"Created {output}", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
