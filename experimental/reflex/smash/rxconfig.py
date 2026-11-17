from __future__ import annotations

import reflex as rx

config = rx.Config(
    app_name="smash",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
)
