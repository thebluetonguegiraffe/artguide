"""ArtGuide — Reflex frontend entry point."""
import reflex as rx

from artguide_app.pages.landing import landing
from artguide_app.pages.app_page import app_page
from artguide_app import styles as s

FONTS = (
    "https://fonts.googleapis.com/css2"
    "?family=Newsreader:ital,wght@0,400;0,500;0,600;1,400;1,500"
    "&family=Work+Sans:wght@400;500;600"
    "&family=IBM+Plex+Mono:wght@400;500"
    "&display=swap"
)

app = rx.App(
    style=s.BASE_STYLE,
    stylesheets=[FONTS, "/global.css"],
    head_components=[
        rx.el.meta(
            name="viewport",
            content="width=device-width, initial-scale=1, viewport-fit=cover",
        ),
        rx.el.meta(name="theme-color", content=s.PAPER),
        rx.el.meta(name="apple-mobile-web-app-capable", content="yes"),
        rx.el.meta(name="mobile-web-app-capable", content="yes"),
        rx.el.meta(name="apple-mobile-web-app-status-bar-style", content="default"),
        rx.el.meta(name="apple-mobile-web-app-title", content="ArtGuide"),
        rx.el.link(rel="apple-touch-icon", href="/apple-touch-icon.png"),
        rx.el.link(
            rel="icon", type="image/png", sizes="192x192",
            href="/android-chrome-192x192.png",
        ),
        rx.el.link(
            rel="icon", type="image/png", sizes="512x512",
            href="/android-chrome-512x512.png",
        ),
        rx.el.link(rel="manifest", href="/site.webmanifest"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=""),
    ],
)

app.add_page(
    landing,
    route="/",
    title="ArtGuide",
    description=(
        "ArtGuide recognises an artwork in seconds and generates a complete, "
        "personalised audio guide."
    ),
)
app.add_page(
    app_page,
    route="/app",
    title="ArtGuide",
    description="Point your camera at an artwork and hear its story.",
)
