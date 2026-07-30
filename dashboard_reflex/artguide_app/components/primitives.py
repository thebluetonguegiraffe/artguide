"""Reusable pieces of the ArtGuide visual language."""
import reflex as rx

from artguide_app import styles as s


def mark(size: int = 30, ink: str = s.INK, dot: bool = True) -> rx.Component:
    """The ArtGuide mark: ink bracket top-left, rust bracket bottom-right."""
    bw = "3px" if size >= 26 else "2px"
    children = [
        rx.box(
            position="absolute",
            top="0",
            left="0",
            width="58%",
            height="58%",
            border_top=f"{bw} solid {ink}",
            border_left=f"{bw} solid {ink}",
        ),
        rx.box(
            position="absolute",
            bottom="0",
            right="0",
            width="58%",
            height="58%",
            border_bottom=f"{bw} solid {s.RUST}",
            border_right=f"{bw} solid {s.RUST}",
        ),
    ]
    if dot:
        children.append(
            rx.box(
                position="absolute",
                top="36%",
                left="36%",
                width="28%",
                height="28%",
                border_radius="50%",
                background_color=ink,
            )
        )
    return rx.box(
        *children,
        position="relative",
        width=f"{size}px",
        height=f"{size}px",
        flex="none",
    )


def wordmark(size: int = 30, ink: str = s.INK, font_size: str = "19px") -> rx.Component:
    """Mark + italic serif 'ArtGuide' lockup."""
    return rx.hstack(
        mark(size, ink),
        rx.text(
            "ArtGuide",
            font_family=s.SERIF,
            font_style="italic",
            font_weight="500",
            font_size=font_size,
            color=ink,
            line_height="1",
        ),
        spacing="0",
        gap="10px",
        align="center",
    )


def label(text, color: str = s.FAINT, **props) -> rx.Component:
    """Uppercase monospace eyebrow label."""
    return rx.text(text, **s.LABEL, color=color, **props)


def corner_frame(*children, accent_size: str = "18px", **props) -> rx.Component:
    """A rounded surface with the bracket motif in two opposite corners."""
    return rx.box(
        rx.box(
            position="absolute",
            top="8px",
            left="8px",
            width=accent_size,
            height=accent_size,
            border_top=f"2px solid {s.INK}",
            border_left=f"2px solid {s.INK}",
        ),
        rx.box(
            position="absolute",
            bottom="8px",
            right="8px",
            width=accent_size,
            height=accent_size,
            border_bottom=f"2px solid {s.RUST}",
            border_right=f"2px solid {s.RUST}",
        ),
        *children,
        position="relative",
        border_radius="12px",
        overflow="hidden",
        **props,
    )


def section_heading(text, max_width: str = "560px", size: str = "32px", **props) -> rx.Component:
    defaults = {
        "font_size": ["25px", "28px", size],
        "line_height": "1.2",
        "color": s.INK,
        "max_width": max_width,
        "margin": "0",
    }
    defaults.update(props)
    return rx.heading(
        text,
        as_="h2",
        font_family=s.SERIF,
        font_weight="400",
        **defaults,
    )


def body(text, size: str = "13px", color: str = s.MUTED, **props) -> rx.Component:
    defaults = {
        "font_size": size,
        "line_height": "1.6",
        "color": color,
        "margin": "0",
    }
    defaults.update(props)
    return rx.text(text, font_family=s.SANS, **defaults)


def primary_button(text, **props) -> rx.Component:
    defaults = {"padding": "14px 26px", "font_size": "13px"}
    defaults.update(props)
    return rx.box(
        text,
        background_color=s.RUST,
        color=s.PAPER,
        font_family=s.SANS,
        font_weight="500",
        border_radius="9px",
        white_space="nowrap",
        cursor="pointer",
        display="inline-block",
        text_align="center",
        transition="background-color .2s ease, transform .2s ease",
        _hover={"background_color": s.RUST_DARK, "transform": "translateY(-1px)"},
        **defaults,
    )


def wrap(*children, **props) -> rx.Component:
    """Centered max-width content column used across the landing page."""
    return rx.box(
        *children,
        max_width=s.WRAP,
        margin="0 auto",
        padding_x=["24px", "32px", "40px"],
        width="100%",
        **props,
    )
