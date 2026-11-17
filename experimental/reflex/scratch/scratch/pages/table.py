"""The table page."""

from __future__ import annotations

import reflex as rx

from scratch.backend.table_state import TableState
from scratch.templates import template
from scratch.views.table import main_table


@template(route="/table", title="Table", on_load=TableState.load_entries)
def table() -> rx.Component:
    """The table page.

    Returns
    -------
        The UI for the table page.

    """
    return rx.vstack(
        rx.heading("Table", size="5"),
        main_table(),
        spacing="8",
        width="100%",
    )
