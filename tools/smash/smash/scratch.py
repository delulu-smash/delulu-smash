"""Welcome to Reflex! This file outlines the steps to create a basic app."""

from __future__ import annotations

import reflex as rx
from rxconfig import config

# from util.const import STAGING_ASSETS_DIR

# gif = "mii_gunner_dtilt_mine.gif"


# class State(rx.State):
#     """The app state."""


# def index() -> rx.Component:
#     # Welcome Page (Index)
#     return rx.container(
#         rx.color_mode.button(position="top-right"),
#         rx.vstack(
#             rx.heading("Welcome to Reflex!", size="9"),
#             rx.text(
#                 "Get started by editing ",
#                 rx.code(f"{config.app_name}/{config.app_name}.py"),
#                 size="5",
#             ),
#             rx.link(
#                 rx.button("Check out our docs!"),
#                 href="https://reflex.dev/docs/getting-started/introduction/",
#                 is_external=True,
#             ),
#             spacing="5",
#             justify="center",
#             min_height="85vh",
#         ),
#         rx.text(f"{gif}"),
#         rx.el.img(src=gif),
#         rx.video(
#             src="https://www.youtube.com/embed/9bZkp7q19f0",
#             width="400px",
#             height="auto",
#         ),
#     )


# Pre-processed data (to avoid the 'rsplit' error from before)
video_data = [
    {
        "name": "Reflex Intro",
        "url": "https://www.youtube.com/watch?v=WryzMcNEfts",
        "thumb": "https://img.youtube.com/vi/WryzMcNEfts/mqdefault.jpg",
    },
]


def video_popup(video: dict) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.button("Watch", variant="classic", cursor="pointer")),
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.dialog.title(video["name"], margin="0"),
                    rx.spacer(),
                    rx.dialog.close(rx.button(rx.icon("x"), variant="soft", color_scheme="gray")),
                    width="100%",
                    align="center",
                ),
                # The Video Player - scaled to look "Large Screen"
                rx.video(
                    url=video["url"],
                    width="100%",
                    height="75vh",  # 75% of the screen height
                    border_radius="10px",
                ),
                width="100%",
                spacing="4",
            ),
            # This makes the actual popup container huge
            style={
                "max_width": "95vw",  # 95% of screen width
                "height": "90vh",  # 90% of screen height
                "padding": "20px",
            },
        ),
    )


def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("Video Gallery", size="8"),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Thumbnail"),
                        rx.table.column_header_cell("Title"),
                        rx.table.column_header_cell("Action"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(
                        video_data,
                        lambda video: rx.table.row(
                            rx.table.cell(rx.image(src=video["thumb"], width="120px")),
                            rx.table.cell(rx.text(video["name"])),
                            rx.table.cell(video_popup(video)),
                            align="center",
                        ),
                    )
                ),
                width="800px",
            ),
            padding_top="5vh",
        ),
        width="100%",
    )


app = rx.App()
app.add_page(index)
