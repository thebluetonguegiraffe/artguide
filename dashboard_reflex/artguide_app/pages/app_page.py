"""The ArtGuide tool: phone viewfinder on mobile, two-column workspace on desktop."""
import reflex as rx

from artguide_app.state import State
from artguide_app.components.primitives import wordmark, label
from artguide_app.components.appbits import (
    settings_panel, gear_button, audio_player, camera_video, player_script,
)
from artguide_app import scripts, styles as s

FRAME_W = "440px"
ACCEPT = {"image/png": [".png"], "image/jpeg": [".jpg", ".jpeg"]}
STRIPES = "repeating-linear-gradient(135deg,#faf8f4 0 10px,#f2efe9 10px 20px)"
ART_STRIPES = "repeating-linear-gradient(135deg,#f7f3ee 0 12px,#efe6dc 12px 24px)"

# Separate video element ids for the mobile and desktop layouts: both are
# always mounted (one hidden via responsive `display`), so a shared id would
# make getElementById silently grab whichever renders first in the DOM.
CAM_MOBILE = "ag-cam-m"
CAM_DESKTOP = "ag-cam-d"

_STOP_ALL_CAMERAS = [
    rx.call_script(scripts.stop_camera_script(CAM_MOBILE)),
    rx.call_script(scripts.stop_camera_script(CAM_DESKTOP)),
]


def _upload(*children, upload_id: str, **props) -> rx.Component:
    defaults = {
        "border": "none",
        "padding": "0",
        "background": "transparent",
        "cursor": "pointer",
    }
    defaults.update(props)
    return rx.upload(
        *children,
        id=upload_id,
        accept=ACCEPT,
        max_files=1,
        multiple=False,
        on_drop=State.handle_upload(rx.upload_files(upload_id=upload_id)),
        **defaults,
    )


def _brackets(tl: str, br: str, size: str = "44px", w: str = "3px",
              pulse: bool = False) -> rx.Component:
    def c(delay: float, **edges) -> rx.Component:
        st = {"animation": f"ag-pulse 1.4s ease-in-out infinite {delay}s"} if pulse else {}
        return rx.box(position="absolute", width=size, height=size, style=st, **edges)

    return rx.fragment(
        c(0, top="0", left="0", border_top=f"{w} solid {tl}", border_left=f"{w} solid {tl}"),
        c(0.2, top="0", right="0", border_top=f"{w} solid {tl}", border_right=f"{w} solid {tl}"),
        c(0.4, bottom="0", left="0", border_bottom=f"{w} solid {br}",
          border_left=f"{w} solid {br}"),
        c(0.6, bottom="0", right="0", border_bottom=f"{w} solid {br}",
          border_right=f"{w} solid {br}"),
    )


def _artwork_frame(
    bracket: str = "16px", radius: str = "10px", ratio: str = "16/11", **props
) -> rx.Component:
    return rx.box(
        rx.box(position="absolute", top="8px", left="8px", width=bracket, height=bracket,
               border_top=f"2px solid {s.INK}", border_left=f"2px solid {s.INK}",
               z_index="1"),
        rx.box(position="absolute", bottom="8px", right="8px", width=bracket,
               height=bracket, border_bottom=f"2px solid {s.RUST}",
               border_right=f"2px solid {s.RUST}", z_index="1"),
        rx.image(src=State.shot, width="100%", height="100%", object_fit="cover"),
        position="relative", width="100%", aspect_ratio=ratio,
        border_radius=radius, overflow="hidden", background=ART_STRIPES, **props,
    )


def _byline(size: str = "12px") -> rx.Component:
    return rx.cond(
        State.artist != "",
        rx.text(
            rx.text.span(State.artist),
            rx.cond(State.year != "", rx.text.span(" · " + State.year)),
            font_family=s.SANS, font_size=size, color=s.SUBTLE,
        ),
    )


def _inline_error(text) -> rx.Component:
    return rx.hstack(
        rx.icon("circle-alert", size=15, color=s.RUST, stroke_width=1.8, flex="none"),
        label(text, color=s.RUST),
        spacing="2", align="center",
    )


def _narration(large: bool = False) -> rx.Component:
    return rx.cond(
        State.audio_generating,
        rx.hstack(
            rx.spinner(size="1", color=s.RUST),
            label(State.t["generating_audio"], color=s.FAINT),
            spacing="2", align="center",
        ),
        rx.cond(
            State.audio_error,
            _inline_error(State.t["audio_error"]),
            rx.cond(
                State.audio_src != "",
                rx.box(audio_player(large=large), class_name="ag-enter-down", width="100%"),
            ),
        ),
    )


def _new_search() -> rx.Component:
    return rx.center(
        rx.text(
            State.t["new_search"], font_family=s.SANS, font_size="13px",
            font_weight="500", color=s.PAPER,
        ),
        on_click=[*_STOP_ALL_CAMERAS, State.restart],
        background_color=s.INK, border_radius="9px", padding="14px",
        width="100%", cursor="pointer", margin_top="18px",
        _hover={"background_color": s.RUST},
        transition="background-color .2s ease",
    )


# =========================================================================== #
# MOBILE
# =========================================================================== #
def _m_header(dark: bool) -> rx.Component:
    ink = s.ON_DARK if dark else s.INK
    return rx.hstack(
        rx.link(wordmark(20, ink=ink, font_size="13px"), href="/", _hover={}),
        rx.spacer(),
        gear_button(dark, size=30),
        align="center",
        width="100%",
        padding="0 22px",
    )


def _m_header_bar(dark: bool) -> rx.Component:
    return rx.box(
        _m_header(dark=dark),
        settings_panel(
            dark=dark,
            position_props={"position": "absolute", "top": "100%", "right": "22px"},
            width="230px",
        ),
        position="relative", padding_top="46px", z_index="3",
    )


def _m_viewfinder() -> rx.Component:
    return rx.fragment(
        rx.box(
            camera_video(CAM_MOBILE),
            style={"display": rx.cond(State.camera_on, "block", "none")},
            position="absolute", inset="0", overflow="hidden",
            background="repeating-linear-gradient(115deg,rgba(255,255,255,.03) 0 2px,transparent 2px 26px)",  # noqa: E501
        ),
        rx.box(
            _brackets(s.ON_DARK, s.RUST),
            rx.center(
                rx.cond(
                    State.camera_on,
                    rx.fragment(),
                    rx.vstack(
                        rx.text(
                            State.t["frame_artwork"], font_family=s.MONO,
                            font_size="11px", font_weight="500",
                            color=s.ON_DARK_FAINT, text_align="center",
                        ),
                        rx.box(
                            State.t["enable_camera"],
                            on_click=rx.call_script(
                                scripts.start_camera_script(CAM_MOBILE),
                                callback=State.camera_started,
                            ),
                            cursor="pointer", font_family=s.SANS, font_size="12px",
                            font_weight="500", color=s.ON_DARK,
                            border=f"1px solid {s.ON_DARK_MUTED}",
                            border_radius="8px", padding="10px 18px",
                            _hover={"background_color": "rgba(255,255,255,.1)"},
                        ),
                        rx.cond(
                            State.camera_error,
                            rx.text(
                                State.camera_message, font_family=s.SANS,
                                font_size="11px", color=s.RUST, text_align="center",
                                max_width="220px",
                            ),
                        ),
                        spacing="3", align="center",
                    ),
                ),
                position="absolute", inset="0",
            ),
            position="absolute", top="130px", left="40px", right="40px", bottom="170px",
        ),
        rx.vstack(
            rx.center(
                rx.box(
                    width="58px", height="58px", border_radius="50%",
                    background_color=s.RUST,
                ),
                on_click=rx.call_script(
                    scripts.capture_script(CAM_MOBILE), callback=State.capture_photo
                ),
                width="74px", height="74px", border_radius="50%",
                border=f"4px solid {s.ON_DARK}", cursor="pointer",
                opacity=rx.cond(State.camera_on, "1", "0.4"),
                pointer_events=rx.cond(State.camera_on, "auto", "none"),
                _hover={"transform": "scale(1.04)"},
                transition="transform .12s ease, opacity .2s ease",
            ),
            _upload(
                rx.text(
                    State.t["upload_photo"], font_family=s.SANS, font_size="12px",
                    color=s.ON_DARK_MUTED,
                    border_bottom=f"1px solid {s.ON_DARK_MUTED}", padding_bottom="2px",
                    _hover={"color": s.ON_DARK},
                ),
                upload_id="m_upload", width="auto",
            ),
            spacing="4", align="center",
            position="absolute", bottom="46px", left="0", right="0",
        ),
    )


def _m_analysing() -> rx.Component:
    dot = {"width": "6px", "height": "6px", "border_radius": "50%",
           "background_color": s.RUST}
    return rx.fragment(
        rx.box(
            rx.image(src=State.shot, width="100%", height="100%",
                     object_fit="cover", opacity="0.3"),
            position="absolute", inset="0", overflow="hidden",
        ),
        rx.box(
            _brackets(s.RUST, s.RUST, pulse=True),
            position="absolute", top="130px", left="40px", right="40px", bottom="170px",
        ),
        rx.vstack(
            rx.text(
                State.t["analysing"] + "…", font_family=s.MONO, font_size="12px",
                font_weight="500", letter_spacing=".06em", color=s.ON_DARK,
            ),
            rx.hstack(
                rx.box(**dot, style={"animation": "ag-pulse 1s infinite"}),
                rx.box(**dot, style={"animation": "ag-pulse 1s infinite .2s"}),
                rx.box(**dot, style={"animation": "ag-pulse 1s infinite .4s"}),
                spacing="0", gap="6px",
            ),
            spacing="3", align="center",
            position="absolute", bottom="78px", left="0", right="0",
        ),
    )


def _m_result() -> rx.Component:
    return rx.vstack(
        _artwork_frame(),
        rx.vstack(
            rx.heading(
                State.title, as_="h1", font_family=s.SERIF, font_weight="500",
                font_size="20px", line_height="1.25", margin="6px 0 2px", color=s.INK,
            ),
            _byline(),
            rx.box(_narration(), margin_top="10px", width="100%"),
            rx.cond(
                State.museum != "",
                label(State.museum, color=s.GHOST, margin_top="6px"),
            ),
            rx.cond(
                State.description != "",
                rx.text(
                    State.description, font_family=s.SANS, font_size="12.5px",
                    line_height="1.6", color="rgba(0,0,0,.6)", margin="12px 0 0",
                ),
                rx.cond(
                    State.description_error,
                    rx.box(_inline_error(State.t["description_error"]), margin_top="12px"),
                ),
            ),
            spacing="0", align="start", width="100%", padding_top="18px",
        ),
        rx.spacer(),
        _new_search(),
        spacing="0", width="100%", padding="18px 22px 34px", flex="1", align="start",
    )


def _m_error() -> rx.Component:
    return rx.vstack(
        _artwork_frame(opacity="0.55"),
        rx.vstack(
            rx.heading(
                State.t["unknown"], as_="h1", font_family=s.SERIF, font_weight="500",
                font_size="20px", margin="0 0 8px", color=s.INK,
            ),
            rx.text(
                State.t["retry"], font_family=s.SANS, font_size="13px",
                line_height="1.6", color=s.MUTED,
            ),
            spacing="0", align="start", width="100%", padding_top="20px",
        ),
        rx.spacer(),
        _new_search(),
        spacing="0", width="100%", padding="18px 22px 34px", flex="1", align="start",
    )


def _mobile() -> rx.Component:
    """Phone experience: dark viewfinder → analysing → light result."""
    capturing = (State.stage == "idle") | (State.stage == "analyzing")
    return rx.box(
        rx.box(
            rx.box(
                _m_header_bar(dark=True),
                rx.match(State.stage, ("analyzing", _m_analysing()), _m_viewfinder()),
                width="100%", max_width=FRAME_W, min_height="100dvh",
                margin="0 auto", position="relative",
                display="flex", flex_direction="column",
            ),
            background=s.DARK_GRADIENT, min_height="100dvh", width="100%",
            display=rx.cond(capturing, "block", "none"),
        ),
        rx.box(
            rx.box(
                _m_header_bar(dark=False),
                rx.match(State.stage, ("error", _m_error()), _m_result()),
                width="100%", max_width=FRAME_W, min_height="100dvh",
                margin="0 auto", display="flex", flex_direction="column",
            ),
            class_name=rx.cond(capturing, "", "ag-enter-up"),
            background_color=s.PAPER, min_height="100dvh", width="100%",
            display=rx.cond(capturing, "none", "block"),
        ),
        display=["block", "block", "none"],
        width="100%",
    )


# =========================================================================== #
# DESKTOP
# =========================================================================== #
def _d_header() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.link(wordmark(24, font_size="16px"), href="/", _hover={}),
            rx.spacer(),
            rx.box(
                gear_button(dark=False, size=38),
                settings_panel(
                    dark=False,
                    position_props={
                        "position": "absolute", "top": "calc(100% + 10px)", "right": "0",
                    },
                    width="250px",
                ),
                position="relative",
            ),
            align="center", width="100%",
        ),
        flex="none",
        margin_bottom="28px",
    )


def _d_left_shell(*content, bg: str = s.PAPER, **props) -> rx.Component:
    return rx.box(
        _d_header(),
        *content,
        padding="32px 36px",
        display="flex",
        flex_direction="column",
        border_right=f"1px solid {s.LINE_SOFT}",
        background_color=bg,
        height="100%",
        min_height="0",
        overflow="hidden",
        **props,
    )


def _d_right_shell(*content, dark: bool = False, **props) -> rx.Component:
    defaults = dict(
        color=s.PAPER if dark else s.INK,
        background=(
            "linear-gradient(160deg,#1a1a1a 0%,#2a2622 100%)" if dark else s.PAPER
        ),
    )
    defaults.update(props)
    return rx.box(
        *content,
        position="relative",
        overflow="hidden",
        display="flex",
        flex_direction="column",
        padding="32px 40px",
        height="100%",
        min_height="0",
        **defaults,
    )


def _d_dropzone() -> rx.Component:
    return _upload(
        rx.fragment(
            _brackets(s.INK, s.RUST, size="22px", w="2px"),
            rx.vstack(
                rx.center(
                    rx.icon("image-up", size=22, color=s.RUST, stroke_width=1.8),
                    width="52px", height="52px", border_radius="50%",
                    background_color=s.PAPER, border=f"1px solid {s.LINE}",
                ),
                rx.vstack(
                    rx.text(
                        State.t["drag_here"], font_family=s.SANS, font_size="15px",
                        font_weight="500",
                    ),
                    rx.text(
                        State.t["file_hint"], font_family=s.SANS, font_size="12.5px",
                        color=s.SUBTLE,
                    ),
                    spacing="1", align="center",
                ),
                rx.hstack(
                    rx.box(
                        State.t["choose_file"],
                        on_click=rx.call_script(scripts.click_file_input_script("d_upload")),
                        background_color=s.RUST, color=s.PAPER,
                        font_family=s.SANS, font_size="13px", font_weight="500",
                        padding="14px 24px", border_radius="9px", cursor="pointer",
                        _hover={"background_color": s.RUST_DARK},
                        transition="background-color .2s ease",
                    ),
                    rx.text(
                        State.t["or"], font_family=s.MONO, font_size="11px",
                        font_weight="500", letter_spacing=".06em", color=s.FAINT,
                    ),
                    rx.box(
                        State.t["use_camera"],
                        on_click=rx.call_script(
                            scripts.start_camera_script(CAM_DESKTOP),
                            callback=State.camera_started,
                        ),
                        cursor="pointer",
                        font_family=s.SANS, font_size="12px",
                        font_weight="500", color=s.MUTED,
                        border_bottom=f"1px solid {s.GHOST}", padding_bottom="4px",
                        _hover={"color": s.INK},
                    ),
                    spacing="0", gap="14px", align="center",
                ),
                rx.cond(
                    State.camera_error,
                    rx.text(
                        State.camera_message, font_family=s.SANS,
                        font_size="12px", color=s.RUST,
                    ),
                ),
                spacing="5", align="center", justify="center", height="100%",
            ),
        ),
        upload_id="d_upload",
        no_click=True,
        no_keyboard=True,
        position="absolute",
        inset="0",
        border="1.5px dashed rgba(0,0,0,.22)",
        border_radius="14px",
        background=STRIPES,
        display=rx.cond(State.camera_on, "none", "flex"),
        align_items="center",
        justify_content="center",
        text_align="center",
        padding="28px",
        width="100%",
        _hover={"border_color": s.RUST},
        transition="border-color .2s ease",
    )


def _d_capture_area() -> rx.Component:
    """Dropzone and live viewfinder stacked in one box.

    The <video> is mounted unconditionally (just hidden via CSS when idle):
    `getUserMedia` runs client-side and looks the element up by id *before*
    the State round-trip flips `camera_on`, so rendering it conditionally
    deadlocked — the script found nothing, returned false, and the camera
    could never turn on.
    """
    return rx.box(
        rx.box(
            camera_video(CAM_DESKTOP),
            _brackets(s.ON_DARK, s.RUST, size="26px", w="2px"),
            rx.vstack(
                rx.center(
                    rx.box(
                        width="52px", height="52px", border_radius="50%",
                        background_color=s.RUST,
                    ),
                    on_click=rx.call_script(
                        scripts.capture_script(CAM_DESKTOP),
                        callback=State.capture_photo,
                    ),
                    width="66px", height="66px", border_radius="50%",
                    border=f"3px solid {s.ON_DARK}", cursor="pointer",
                    _hover={"transform": "scale(1.05)"},
                    transition="transform .12s ease",
                ),
                rx.box(
                    State.t["back"],
                    on_click=[
                        rx.call_script(scripts.stop_camera_script(CAM_DESKTOP)),
                        State.set_camera_on(False),
                    ],
                    cursor="pointer", font_family=s.SANS, font_size="12px",
                    color=s.ON_DARK_MUTED,
                    border_bottom=f"1px solid {s.ON_DARK_MUTED}",
                    _hover={"color": s.ON_DARK},
                ),
                spacing="3", align="center",
                position="absolute", bottom="20px", left="0", right="0",
            ),
            position="absolute", inset="0",
            display=rx.cond(State.camera_on, "block", "none"),
            border_radius="14px", overflow="hidden", background="#000",
        ),
        _d_dropzone(),
        position="relative", flex="1", min_height="200px", width="100%",
    )


def _d_left_idle() -> rx.Component:
    return _d_left_shell(
        rx.box(
            label(State.t["recognise_artwork"], color=s.RUST, margin_bottom="10px"),
            rx.heading(
                State.t["upload_h1"],
                rx.text.span(State.t["upload_h1_em"], font_style="italic", color=s.RUST),
                ".",
                as_="h1", font_family=s.SERIF, font_weight="400", font_size="28px",
                line_height="1.2", margin="0 0 24px", max_width="400px",
            ),
            display=rx.cond(State.camera_on, "none", "block"),
            flex="none",
        ),
        _d_capture_area(),
    )


def _scan_rings() -> rx.Component:
    ring = {
        "position": "absolute", "top": "50%", "left": "50%",
        "width": "100%", "height": "100%", "border_radius": "50%",
        "border": "1px solid rgba(200,52,31,.4)",
    }
    return rx.center(
        rx.box(
            rx.box(**ring, style={
                "animation": "ag-ring-expand 3s ease-out infinite",
                "transform": "translate(-50%,-50%)"}),
            rx.box(**ring, style={
                "animation": "ag-ring-expand 3s ease-out infinite 1s",
                "transform": "translate(-50%,-50%)"}),
            rx.box(**ring, style={
                "animation": "ag-ring-expand 3s ease-out infinite 2s",
                "transform": "translate(-50%,-50%)"}),
            rx.box(
                _brackets(s.ON_DARK, s.RUST, size="34px", w="2px"),
                rx.box(
                    position="absolute", top="50%", left="50%",
                    transform="translate(-50%,-50%)", width="14px", height="14px",
                    border_radius="50%", background_color=s.RUST,
                    box_shadow="0 0 20px rgba(200,52,31,.7)",
                ),
                position="relative", width="120px", height="120px",
            ),
            position="relative", width="220px", height="220px",
            display="flex", align_items="center", justify_content="center",
        ),
        position="relative", z_index="1", flex="1",
    )


def _dark_blobs() -> rx.Component:
    return rx.fragment(
        rx.box(
            position="absolute", top="-80px", right="-80px", width="340px",
            height="340px", border_radius="50%",
            background="radial-gradient(circle,rgba(200,52,31,.35),transparent 70%)",
            filter="blur(8px)",
            style={"animation": "ag-float-a 9s ease-in-out infinite"},
        ),
        rx.box(
            position="absolute", bottom="-100px", left="-60px", width="280px",
            height="280px", border_radius="50%",
            background="radial-gradient(circle,rgba(200,52,31,.18),transparent 70%)",
            filter="blur(8px)",
            style={"animation": "ag-float-b 11s ease-in-out infinite"},
        ),
    )


def _d_right_idle() -> rx.Component:
    """Dark side panel: rotating marketing phrases + the idle scan animation."""
    return _d_right_shell(
        _dark_blobs(),
        rx.box(
            label(State.t["while_waiting"], color="rgba(255,254,252,.5)",
                  margin_bottom="14px"),
            rx.box(
                rx.foreach(
                    State.waiting_phrases,
                    lambda p: rx.text(
                        p["before"],
                        rx.text.span(p["em"], font_style="italic", color=s.RUST),
                        p["after"],
                        position="absolute", inset="0",
                        font_family=s.SERIF, font_weight="400",
                        font_size="22px", line_height="1.3", opacity="0",
                        style={
                            "animation": "ag-phrase 12s ease-in-out infinite",
                            "animation_delay": p["delay"],
                        },
                    ),
                ),
                position="relative", height="90px", overflow="hidden",
            ),
            position="relative", z_index="1", flex="none",
        ),
        _scan_rings(),
        dark=True,
    )


def _d_right_analysing() -> rx.Component:
    dot = {"width": "6px", "height": "6px", "border_radius": "50%",
           "background_color": s.RUST}
    return _d_right_shell(
        _dark_blobs(),
        rx.box(
            label(State.t["analysing"], color="rgba(255,254,252,.55)"),
            rx.hstack(
                rx.box(**dot, style={"animation": "ag-pulse 1s infinite"}),
                rx.box(**dot, style={"animation": "ag-pulse 1s infinite .2s"}),
                rx.box(**dot, style={"animation": "ag-pulse 1s infinite .4s"}),
                spacing="0", gap="6px", margin_top="10px",
            ),
            position="relative", z_index="1", flex="none",
        ),
        _scan_rings(),
        dark=True,
        class_name="ag-enter-left-delayed",
    )


def _d_left_analysing() -> rx.Component:
    return _d_left_shell(
        rx.box(
            rx.image(
                src=State.shot, width="100%", height="100%",
                object_fit="cover", opacity="0.4",
            ),
            _brackets(s.RUST, s.RUST, size="26px", w="2px", pulse=True),
            position="relative", flex="1", border_radius="12px",
            overflow="hidden", background=ART_STRIPES,
        ),
        class_name="ag-enter-left",
    )


def _d_left_result() -> rx.Component:
    return _d_left_shell(
        _artwork_frame(bracket="26px", radius="12px", ratio="4/5", flex="1"),
        bg=s.SAND,
        class_name="ag-enter-left",
    )


def _d_right_result() -> rx.Component:
    return _d_right_shell(
        rx.box(
            rx.match(
                State.stage,
                (
                    "error",
                    rx.vstack(
                        label(State.t["unknown"], color=s.RUST, margin_bottom="10px"),
                        rx.heading(
                            State.t["unknown"], as_="h1", font_family=s.SERIF,
                            font_weight="400", font_size="34px", line_height="1.15",
                            margin="0 0 6px",
                        ),
                        rx.text(
                            State.t["retry"], font_family=s.SANS, font_size="14px",
                            line_height="1.7", color="rgba(0,0,0,.72)", margin_top="8px",
                        ),
                        spacing="0", align="start", width="100%",
                    ),
                ),
                rx.vstack(
                    rx.box(
                        label(State.t["recognised"], color=s.RUST, margin_bottom="8px"),
                        rx.heading(
                            State.title, as_="h1", font_family=s.SERIF, font_weight="400",
                            font_size="34px", line_height="1.15", margin="0 0 4px",
                        ),
                        rx.cond(
                            State.artist != "",
                            rx.text(
                                rx.text.span(State.artist),
                                rx.cond(
                                    State.year != "", rx.text.span(" · " + State.year)
                                ),
                                font_family=s.SANS, font_size="14px", color=s.MUTED,
                            ),
                        ),
                        width="100%",
                    ),
                    _narration(large=True),
                    rx.cond(State.museum != "", label(State.museum, color=s.SUBTLE)),
                    rx.cond(
                        State.description != "",
                        rx.text(
                            State.description, font_family=s.SANS, font_size="14px",
                            line_height="1.7", color="rgba(0,0,0,.72)",
                            style={"text_wrap": "pretty"},
                        ),
                        rx.cond(
                            State.description_error,
                            _inline_error(State.t["description_error"]),
                        ),
                    ),
                    spacing="3", align="start", width="100%",
                ),
            ),
            flex="1", min_height="0", overflow_y="auto", width="100%",
        ),
        rx.box(
            rx.center(
                rx.text(
                    State.t["new_search"], font_family=s.SANS, font_size="13px",
                    font_weight="500", color=s.PAPER,
                ),
                on_click=[*_STOP_ALL_CAMERAS, State.restart],
                background_color=s.INK, border_radius="9px", padding="14px 24px",
                cursor="pointer", display="inline-flex",
                _hover={"background_color": s.RUST},
                transition="background-color .2s ease",
            ),
            flex="none", margin_top="16px",
        ),
        dark=False,
        class_name="ag-enter-left-delayed",
    )


def _d_grid(left: rx.Component, right: rx.Component) -> rx.Component:
    return rx.grid(
        left, right,
        grid_template_columns="1fr 1fr",
        height="100dvh",
        width="100%",
        overflow="hidden",
    )


def _desktop() -> rx.Component:
    return rx.box(
        rx.match(
            State.stage,
            ("analyzing", _d_grid(_d_left_analysing(), _d_right_analysing())),
            ("error", _d_grid(_d_left_result(), _d_right_result())),
            ("result", _d_grid(_d_left_result(), _d_right_result())),
            _d_grid(_d_left_idle(), _d_right_idle()),
        ),
        display=["none", "none", "block"],
        width="100%",
        height="100dvh",
        overflow="hidden",
        background_color=s.BONE,
    )


# =========================================================================== #
def app_page() -> rx.Component:
    return rx.fragment(
        player_script(),
        _mobile(),
        _desktop(),
    )
