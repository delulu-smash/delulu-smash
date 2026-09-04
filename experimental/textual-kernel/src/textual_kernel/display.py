"""Jupyter-style rich display for a cell's return value.

``dataframe_view`` recognizes common dataframe types and returns plain
(columns, rows, total_row_count) data for the caller to feed into a Textual
``DataTable``. ``to_renderable`` is a fallback for objects that already
implement Rich's display protocol (e.g. a ``rich.table.Table`` built by
hand); anything else should just be shown via its repr().
"""

from __future__ import annotations

from typing import Any

from rich.console import RenderableType

MAX_ROWS = 500
MAX_COLS = 50

DataFrameView = tuple[list[str], list[tuple[Any, ...]], int]


def to_renderable(value: Any) -> RenderableType | None:
    """Pass through objects that already implement Rich's display protocol."""
    if hasattr(value, "__rich_console__") or hasattr(value, "__rich__"):
        return value
    return None


def dataframe_view(value: Any) -> DataFrameView | None:
    """Return (columns, rows, total_row_count) for known dataframe types."""
    for builder in (_polars_view, _pandas_view):
        view = builder(value)
        if view is not None:
            return view
    return None


def _polars_view(value: Any) -> DataFrameView | None:
    try:
        import polars as pl
    except ImportError:
        return None

    if isinstance(value, pl.Series):
        value = value.to_frame()
    if not isinstance(value, pl.DataFrame):
        return None

    head = value.head(MAX_ROWS)
    columns = list(head.columns)[:MAX_COLS]
    rows = [tuple(_cell_str(v) for v in row[:MAX_COLS]) for row in head.rows()]
    return columns, rows, value.height


def _pandas_view(value: Any) -> DataFrameView | None:
    try:
        import pandas as pd
    except ImportError:
        return None

    if isinstance(value, pd.Series):
        value = value.to_frame()
    if not isinstance(value, pd.DataFrame):
        return None

    head = value.head(MAX_ROWS)
    columns = list(head.columns)[:MAX_COLS]
    rows = [
        tuple(_cell_str(v) for v in row[:MAX_COLS])
        for row in head.itertuples(index=False, name=None)
    ]
    return columns, rows, len(value)


def _cell_str(value: Any) -> str:
    return "" if value is None else str(value)
