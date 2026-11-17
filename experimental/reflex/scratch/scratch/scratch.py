"""Welcome to Reflex!."""

# Import all the pages.
from __future__ import annotations

import reflex as rx

# `pages` is imported for its side effect: the page decorators register routes on import
from scratch import pages, styles

# Create the app.
app = rx.App(
    style=styles.base_style,
    stylesheets=styles.base_stylesheets,
)

__all__ = ["app", "pages"]
