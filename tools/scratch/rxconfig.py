import reflex as rx

config = rx.Config(
    app_name="scratch",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)