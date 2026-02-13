#!/usr/bin/env python3
"""
mp4_to_gif.py — Convert a segment of an MP4 to an animated GIF using ffmpeg.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Optional

import typer

app = typer.Typer(
    name="mp4-to-gif",
    help="🎞️  Convert a sub-selection of an MP4 file to an animated GIF via ffmpeg.",
    add_completion=False,
)


def _check_ffmpeg() -> None:
    """Abort early if ffmpeg is not on PATH."""
    if shutil.which("ffmpeg") is None:
        typer.echo("❌  ffmpeg not found. Install it and make sure it is on your PATH.", err=True)
        raise typer.Exit(code=1)


def _parse_time(value: str, label: str) -> str:
    """
    Accept HH:MM:SS, MM:SS, or plain seconds (int/float).
    Returns the value unchanged — ffmpeg understands all of these natively.
    Raises typer.BadParameter when the format is clearly wrong.
    """
    import re

    # plain number  e.g. "30" or "12.5"
    if re.fullmatch(r"\d+(\.\d+)?", value):
        return value

    # HH:MM:SS or MM:SS
    if re.fullmatch(r"(\d{1,2}:)?\d{1,2}:\d{2}(\.\d+)?", value):
        return value

    raise typer.BadParameter(f"Invalid {label} time '{value}'. Use HH:MM:SS, MM:SS, or seconds (e.g. 30 or 1.5).")


@app.command()
def convert(
    input_file: Path = typer.Argument(
        ...,
        help="Path to the source MP4 file.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    output_file: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Destination GIF path. Defaults to <input_stem>.gif in the same directory.",
    ),
    start: str = typer.Option(
        "0",
        "--start",
        "-s",
        help="Start time of the clip (HH:MM:SS, MM:SS, or seconds). Default: 0.",
    ),
    duration: str | None = typer.Option(
        None,
        "--duration",
        "-d",
        help="Duration of the clip (HH:MM:SS, MM:SS, or seconds). Omit to go to end.",
    ),
    end: str | None = typer.Option(
        None,
        "--end",
        "-e",
        help="End time of the clip (HH:MM:SS, MM:SS, or seconds). Alternative to --duration.",
    ),
    fps: int = typer.Option(
        30,
        "--fps",
        min=1,
        max=60,
        help=(
            "Output frame rate. Playback speed is always correct — "
            "lower fps = choppier motion but smaller file. Default: 30."
        ),
    ),
    width: int = typer.Option(
        480,
        "--width",
        "-w",
        min=16,
        help="Output width in pixels (height scales automatically). Default: 480.",
    ),
    colors: int = typer.Option(
        128,
        "--colors",
        min=2,
        max=256,
        help="Number of palette colors (2-256). Higher = better quality. Default: 128.",
    ),
    loop: int = typer.Option(
        0,
        "--loop",
        min=-1,
        help="GIF loop count: 0 = infinite, -1 = no loop, N = loop N times. Default: 0.",
    ),
    dither: str = typer.Option(
        "bayer",
        "--dither",
        help="Dithering algorithm: none | bayer | floyd_steinberg. Default: bayer.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show the ffmpeg commands being executed.",
    ),
) -> None:
    """
    Convert a specific time range of an MP4 file into a high-quality animated GIF.

    Uses a two-pass palettegen approach for the best colour quality.
    Playback speed always matches the source video — fps only affects smoothness.

    \b

    Examples
    --------
    # Seconds 10-25 of video.mp4
    python mp4_to_gif.py video.mp4 --start 10 --end 25

    # First 8 seconds, 30 fps, 600 px wide
    python mp4_to_gif.py clip.mp4 -s 0 -d 8 --fps 30 --width 600

    # MM:SS timestamps, custom output path
    python mp4_to_gif.py talk.mp4 --start 1:30 --end 2:00 -o highlights.gif
    """
    _check_ffmpeg()

    # ── Validate / resolve times ─────────────────────────────────────────────
    start = _parse_time(start, "start")

    if end and duration:
        typer.echo("❌  Provide --end OR --duration, not both.", err=True)
        raise typer.Exit(code=1)

    if end:
        end = _parse_time(end, "end")
        duration_flag: list[str] = ["-to", end]
    elif duration:
        duration = _parse_time(duration, "duration")
        duration_flag = ["-t", duration]
    else:
        duration_flag = []

    if dither not in {"none", "bayer", "floyd_steinberg"}:
        typer.echo(f"❌  Unknown dither mode '{dither}'. Choose: none | bayer | floyd_steinberg", err=True)
        raise typer.Exit(code=1)

    # ── Resolve output path ──────────────────────────────────────────────────
    if output_file is None:
        output_file = input_file.with_suffix(".gif")

    output_file = output_file.resolve()
    input_file = input_file.resolve()

    # ── Build filter graph ────────────────────────────────────────────────────
    # fps= resamples the source to the target frame rate.
    # -r {fps} on the output tells the GIF muxer to write a frame delay of
    # exactly 1/fps seconds per frame. Without this, ffmpeg can inherit wrong
    # timestamps and write delays that make the GIF play back too slowly.
    scale_filter = f"fps={fps},scale={width}:-1:flags=lanczos"
    palette_filter = f"palettegen=max_colors={colors}"
    paletteuse_filter = f"paletteuse=dither={dither}"

    vf_pass1 = f"{scale_filter}[x];[x]{palette_filter}"
    vf_pass2 = f"{scale_filter}[x];[x][1:v]{paletteuse_filter}"

    # ── Temp palette file ─────────────────────────────────────────────────────
    palette_path = output_file.with_name(output_file.stem + "_palette.png")

    # Shared seek flags (placed before -i for fast keyframe seek)
    seek_flags = ["-ss", start] + duration_flag

    # ── Pass 1: generate palette ──────────────────────────────────────────────
    cmd_pass1 = [
        "ffmpeg",
        "-y",
        *seek_flags,
        "-i",
        str(input_file),
        "-vf",
        vf_pass1,
        "-frames:v",
        "1",
        str(palette_path),
    ]

    typer.echo(f"🎨  Generating palette  →  {palette_path.name}")
    if verbose:
        typer.echo("    " + " ".join(str(c) for c in cmd_pass1))

    result1 = subprocess.run(cmd_pass1, capture_output=not verbose)
    if result1.returncode != 0:
        typer.echo("❌  Palette generation failed.", err=True)
        if not verbose:
            typer.echo(result1.stderr.decode(errors="replace"), err=True)
        raise typer.Exit(code=1)

    # ── Pass 2: render GIF ────────────────────────────────────────────────────
    loop_value = str(loop) if loop >= 0 else "-1"

    cmd_pass2 = [
        "ffmpeg",
        "-y",
        *seek_flags,
        "-i",
        str(input_file),
        "-i",
        str(palette_path),
        "-lavfi",
        vf_pass2,
        "-r",
        str(fps),  # ← forces correct GIF frame delay = 1/fps seconds
        "-loop",
        loop_value,
        str(output_file),
    ]

    typer.echo(f"✂️   Rendering GIF       →  {output_file}")
    if verbose:
        typer.echo("    " + " ".join(str(c) for c in cmd_pass2))

    result2 = subprocess.run(cmd_pass2, capture_output=not verbose)
    palette_path.unlink(missing_ok=True)

    if result2.returncode != 0:
        typer.echo("❌  GIF rendering failed.", err=True)
        if not verbose:
            typer.echo(result2.stderr.decode(errors="replace"), err=True)
        raise typer.Exit(code=1)

    size_mb = output_file.stat().st_size / 1_048_576
    typer.echo(f"✅  Done!  {output_file}  ({size_mb:.2f} MB)")


if __name__ == "__main__":
    app()
