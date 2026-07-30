"""Pieces shared by the mobile and desktop versions of the tool."""
import reflex as rx

from artguide_app.state import State, LANGUAGES
from artguide_app.components.primitives import label
from artguide_app import scripts, styles as s

# Bar heights (percent) for the narration waveform, matching the design.
WAVE = [60, 90, 50, 80, 70, 40, 88, 55, 72, 45, 82, 60, 35, 75, 50, 88, 42, 66,
        58, 78, 44, 62, 84, 48, 36, 70, 52, 86, 40, 68, 54, 80, 46, 74, 58, 42]


# --------------------------------------------------------------------------- #
# Chips
# --------------------------------------------------------------------------- #
def chip(text, active, on_click, dark: bool = False) -> rx.Component:
    """Small selectable pill used throughout the settings panel.

    Colors are set as individual conditional props (background_color, color,
    and a border shorthand with the color Var interpolated via f-string) —
    NOT a single `style={...}` dict swapped by rx.cond, which silently failed
    to apply background/text color on the active chip (rendered as a blank
    box: rust border but no fill and invisible white-on-white text).
    """
    idle_fg = "rgba(255,255,255,.75)" if dark else s.INK
    idle_bd = "rgba(255,255,255,.2)" if dark else s.LINE

    return rx.box(
        text,
        on_click=on_click,
        cursor="pointer",
        display="inline-flex",
        align_items="center",
        padding=["5px 9px", "6px 10px", "7px 12px"],
        border_radius="8px",
        font_family=s.MONO,
        font_size=["9.5px", "10px", "11px"],
        font_weight="500",
        letter_spacing=".06em",
        text_transform="uppercase",
        white_space="nowrap",
        background_color=rx.cond(active, s.RUST, "transparent"),
        color=rx.cond(active, s.PAPER, idle_fg),
        border=f"1px solid {rx.cond(active, s.RUST, idle_bd)}",
        transition="all .15s ease",
    )


def _chip_group(title, chips: list[rx.Component], dark: bool) -> rx.Component:
    return rx.box(
        label(
            title,
            color="rgba(255,255,255,.55)" if dark else "rgba(0,0,0,.55)",
            margin_bottom="8px",
        ),
        rx.flex(*chips, gap="6px", wrap="wrap"),
    )


def settings_body(dark: bool) -> rx.Component:
    """Language / length / voice chip groups."""
    return rx.vstack(
        _chip_group(
            State.t["language"],
            [
                chip(
                    code.upper(),
                    State.language == code,
                    State.set_language(code),
                    dark,
                )
                for code in LANGUAGES
            ],
            dark,
        ),
        _chip_group(
            State.t["description_duration"],
            [
                chip(
                    State.t["short_audio"], State.duration == "short",
                    State.set_duration("short"), dark,
                ),
                chip(
                    State.t["medium_audio"], State.duration == "medium",
                    State.set_duration("medium"), dark,
                ),
                chip(
                    State.t["long_audio"], State.duration == "long",
                    State.set_duration("long"), dark,
                ),
            ],
            dark,
        ),
        _chip_group(
            State.t["speaker"],
            [
                chip(
                    State.t["female_speaker"], State.speaker == "female",
                    State.set_speaker("female"), dark,
                ),
                chip(
                    State.t["male_speaker"], State.speaker == "male",
                    State.set_speaker("male"), dark,
                ),
            ],
            dark,
        ),
        spacing="4",
        width="100%",
        align="start",
    )


# --------------------------------------------------------------------------- #
# Gear button + panel (with click-outside-to-close backdrop)
# --------------------------------------------------------------------------- #
def gear_button(dark: bool, size: int = 38) -> rx.Component:
    ink = s.ON_DARK if dark else s.INK
    border = "rgba(255,255,255,.25)" if dark else "rgba(0,0,0,.14)"
    return rx.box(
        rx.icon("settings", size=int(size * 0.47), color=ink, stroke_width=1.6),
        on_click=State.toggle_settings,
        position="relative",
        width=f"{size}px",
        height=f"{size}px",
        border_radius="10px" if size >= 36 else "8px",
        border=f"1px solid {rx.cond(State.settings_open, s.RUST, border)}",
        background_color="transparent" if dark else s.PAPER,
        display="flex",
        align_items="center",
        justify_content="center",
        cursor="pointer",
        flex="none",
        z_index="21",
        transition="border-color .15s ease",
        _hover={"border_color": s.RUST},
    )


def _settings_backdrop() -> rx.Component:
    """Full-viewport invisible layer behind the panel: click it to close.

    Sits as a sibling *before* the panel at a lower z-index, so the browser's
    own hit-testing routes clicks on the panel to the panel (no propagation
    tricks needed) and clicks anywhere else to this backdrop.
    """
    return rx.cond(
        State.settings_open,
        rx.box(
            position="fixed",
            inset="0",
            z_index="19",
            on_click=State.close_settings,
            cursor="default",
        ),
    )


def settings_panel(dark: bool, *, position_props: dict, width: str = "230px") -> rx.Component:
    """Backdrop + the settings dropdown itself, positioned by the caller."""
    bg = "rgba(20,18,16,.96)" if dark else s.PAPER
    border = "1px solid rgba(255,255,255,.14)" if dark else f"1px solid {s.LINE}"
    return rx.fragment(
        _settings_backdrop(),
        rx.cond(
            State.settings_open,
            rx.box(
                label(State.t["settings"], color=s.RUST, margin_bottom="12px"),
                settings_body(dark=dark),
                width=width,
                background_color=bg,
                backdrop_filter="blur(10px)",
                border=border,
                border_radius="12px",
                box_shadow="0 20px 50px -20px rgba(0,0,0,.5)",
                padding="16px",
                z_index="20",
                **position_props,
            ),
        ),
    )


# --------------------------------------------------------------------------- #
# Live camera capture (mobile viewfinder + desktop in-panel variant share this)
# --------------------------------------------------------------------------- #
def camera_video(video_id: str) -> rx.Component:
    return rx.el.video(
        id=video_id,
        auto_play=True,
        muted=True,
        plays_inline=True,
        custom_attrs={"webkit-playsinline": "true"},
        style={"width": "100%", "height": "100%", "object_fit": "cover"},
    )


# --------------------------------------------------------------------------- #
# Narration player
# --------------------------------------------------------------------------- #
def audio_player(large: bool = False) -> rx.Component:
    """Custom player: play/pause, animated waveform, remaining time.

    Everything is scoped by the `.ag-player` wrapper class (see scripts.py)
    rather than element ids, since this component can be mounted twice at
    once (mobile + desktop layouts both render; only one is visible).
    """
    n = 36 if large else 22
    circle = 52 if large else 38
    tri = "8px 0 8px 12px" if large else "6px 0 6px 9px"
    bar_h = "30px" if large else "22px"

    bars = [
        rx.el.span(
            style={
                "width": "3px",
                "height": f"{h}%",
                "background": "rgba(0,0,0,.28)",
                "border_radius": "2px",
                "animation_delay": f"{i * 0.08:.2f}s",
                "flex": "none",
            }
        )
        for i, h in enumerate(WAVE[:n])
    ]

    return rx.box(
        rx.el.audio(src=State.audio_src, preload="metadata"),
        rx.hstack(
            rx.center(
                rx.box(
                    class_name="ag-tri",
                    width="0",
                    height="0",
                    border_style="solid",
                    border_width=tri,
                    border_color=f"transparent transparent transparent {s.PAPER}",
                    margin_left="3px",
                ),
                rx.hstack(
                    rx.box(width="3px", height="14px", background_color=s.PAPER),
                    rx.box(width="3px", height="14px", background_color=s.PAPER),
                    spacing="0",
                    gap="3px",
                    class_name="ag-pause",
                    display="none",
                ),
                class_name="ag-play",
                width=f"{circle}px",
                height=f"{circle}px",
                border_radius="50%",
                background_color=s.RUST,
                flex="none",
                cursor="pointer",
                transition="background-color .15s ease",
                _hover={"background_color": s.RUST_DARK},
            ),
            rx.flex(
                *bars,
                class_name="ag-bars",
                justify="between",
                align="center",
                height=bar_h,
                flex="1",
                min_width="0",
                gap="2px",
                overflow="hidden",
            ),
            rx.text(
                "0:00",
                class_name="ag-time",
                font_family=s.MONO,
                font_size=["10px", "10px", "11px"],
                font_weight="500",
                letter_spacing=".06em",
                color=s.FAINT,
                flex="none",
            ),
            spacing="0",
            gap=["12px", "14px", "18px"],
            align="center",
            width="100%",
        ),
        class_name="ag-player",
        background_color=s.SAND,
        border=f"1px solid {s.LINE_SOFT}" if large else "none",
        border_radius="14px",
        padding=["14px 16px", "16px 18px", "18px 20px"],
        width="100%",
    )


def player_script() -> rx.Component:
    return rx.script(scripts.AUDIO_PLAYER)
