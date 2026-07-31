"""Marketing landing page."""

import reflex as rx

from artguide_app.state import State, LANGUAGES
from artguide_app.components.primitives import (
    wordmark,
    label,
    corner_frame,
    body,
    primary_button,
    wrap,
)
from artguide_app import scripts, styles as s

STRIPES = "repeating-linear-gradient(135deg,#f7f3ee 0 10px,#efe6dc 10px 20px)"

R = {"data-r": "true"}  # fade + rise on scroll
R_STAGGER = {"data-r-stagger": "true"}  # children rise in sequence
R_CLIP = {"data-clip": "true"}  # clip-path wipe for imagery


# --------------------------------------------------------------------------- #
# Small shared pieces
# --------------------------------------------------------------------------- #
def eyebrow(text, color: str = s.FAINT, **props) -> rx.Component:
    """Mono label whose underline draws itself in when revealed."""
    return label(
        text,
        color=color,
        class_name="lbl-draw",
        custom_attrs=R,
        display="inline-block",
        margin_bottom="10px",
        **props,
    )


def split_heading(
    plain, em, size: str = "32px", max_width: str = "560px", color: str = s.INK, **props
) -> rx.Component:
    """Serif heading ending in an italic rust emphasis."""
    defaults = {
        "font_size": ["25px", "28px", size],
        "line_height": "1.2",
        "color": color,
        "max_width": max_width,
        "margin": "16px 0 0",
    }
    defaults.update(props)
    return rx.heading(
        plain,
        rx.text.span(em, font_style="italic", color=s.RUST),
        ".",
        as_="h2",
        custom_attrs=R,
        font_family=s.SERIF,
        font_weight="400",
        **defaults,
    )


def _shape(shape_var, size: str = "26px") -> rx.Component:
    base = {"width": size, "height": size, "flex": "none"}
    return rx.match(
        shape_var,
        ("circle", rx.box(**base, border=f"2px solid {s.RUST}", border_radius="50%")),
        ("leaf", rx.box(**base, border=f"2px solid {s.RUST}", border_radius="50% 50% 50% 0")),
        ("dashed", rx.box(**base, border=f"2px dashed {s.INK}", border_radius="50%")),
        (
            "bracket_br",
            rx.box(**base, border_bottom=f"2px solid {s.INK}", border_right=f"2px solid {s.INK}"),
        ),
        rx.box(**base, border_top=f"2px solid {s.INK}", border_left=f"2px solid {s.INK}"),
    )


def _blob(anim: str, **props) -> rx.Component:
    return rx.box(
        position="absolute",
        border_radius="50%",
        background="radial-gradient(circle,rgba(200,52,31,.12),transparent 70%)",
        filter="blur(6px)",
        pointer_events="none",
        style={"animation": anim},
        **props,
    )


def _section(*children, bg: str = s.PAPER, bordered: bool = False, **props) -> rx.Component:
    border = f"1px solid {s.LINE_SOFT}"
    defaults = {
        "background_color": bg,
        "border_top": border if bordered else "none",
        "border_bottom": border if bordered else "none",
        "padding_y": ["60px", "72px", "90px"],
    }
    defaults.update(props)
    return rx.box(wrap(*children), **defaults)


def _grid(*children, cols, gap="16px", **props) -> rx.Component:
    return rx.grid(
        *children,
        grid_template_columns=cols,
        gap=gap,
        width="100%",
        custom_attrs=R_STAGGER,
        **props,
    )


# --------------------------------------------------------------------------- #
# Nav
# --------------------------------------------------------------------------- #
def _lang_switch() -> rx.Component:
    def one(code: str) -> rx.Component:
        return rx.box(
            code.upper(),
            on_click=State.set_language(code),
            cursor="pointer",
            font_family=s.MONO,
            font_size="11px",
            font_weight="500",
            letter_spacing=".06em",
            color=rx.cond(State.language == code, s.RUST, s.GHOST),
            transition="color .15s ease",
            _hover={"color": s.INK},
        )

    return rx.hstack(*[one(c) for c in LANGUAGES], spacing="0", gap="10px", align="center")


def _hamburger_button() -> rx.Component:
    return rx.box(
        rx.icon("menu", size=20, color=s.INK, stroke_width=1.8),
        on_click=State.toggle_mobile_nav,
        display=["flex", "flex", "flex", "none"],
        align_items="center",
        justify_content="center",
        width="36px",
        height="36px",
        flex="none",
        cursor="pointer",
    )


def _mobile_nav_menu() -> rx.Component:
    """Backdrop + dropdown holding everything but the wordmark and the CTA."""
    return rx.fragment(
        rx.cond(
            State.mobile_nav_open,
            rx.box(
                position="fixed",
                inset="0",
                z_index="9",
                on_click=State.close_mobile_nav,
                cursor="default",
            ),
        ),
        rx.cond(
            State.mobile_nav_open,
            rx.box(
                rx.vstack(
                    rx.foreach(
                        State.lc_nav,
                        lambda item: rx.link(
                            item["text"],
                            href=item["href"],
                            on_click=State.close_mobile_nav,
                            font_family=s.SANS,
                            font_size="14px",
                            font_weight="500",
                            color=s.MUTED,
                            _hover={"color": s.INK},
                        ),
                    ),
                    rx.box(
                        _lang_switch(),
                        border_top=f"1px solid {s.LINE_SOFT}",
                        padding_top="16px",
                        margin_top="4px",
                        width="100%",
                    ),
                    rx.box(
                        primary_button(
                            State.lc["nav_cta"],
                            padding="10px 20px",
                            width="100%",
                        ),
                        on_click=State.open_contact,
                        display="inline-block",
                        width="100%",
                    ),
                    spacing="4",
                    align="start",
                    width="100%",
                ),
                position="absolute",
                top="100%",
                right="0",
                left="0",
                background_color=s.PAPER,
                border_bottom=f"1px solid {s.LINE_SOFT}",
                box_shadow="0 20px 50px -20px rgba(0,0,0,.3)",
                padding="20px 24px 26px",
                z_index="10",
                display=["block", "block", "block", "none"],
            ),
        ),
    )


def _nav() -> rx.Component:
    return rx.box(
        wrap(
            rx.hstack(
                rx.link(wordmark(30), href="/", _hover={}),
                rx.spacer(),
                rx.hstack(
                    rx.foreach(
                        State.lc_nav,
                        lambda item: rx.link(
                            item["text"],
                            href=item["href"],
                            font_family=s.SANS,
                            font_size="12px",
                            font_weight="500",
                            color=s.MUTED,
                            _hover={"color": s.INK},
                        ),
                    ),
                    spacing="0",
                    gap="26px",
                    display=["none", "none", "none", "flex"],
                ),
                rx.hstack(
                    _lang_switch(),
                    rx.box(
                        primary_button(State.lc["nav_cta"], padding="10px 20px"),
                        on_click=State.open_contact,
                        display="inline-block",
                    ),
                    spacing="0",
                    gap=["14px", "18px", "34px"],
                    align="center",
                    display=["none", "none", "none", "flex"],
                ),
                rx.link(
                    rx.text(
                        State.lc["open_app"],
                        font_family=s.SANS,
                        font_size="12px",
                        font_weight="500",
                        color=s.INK,
                        border_bottom=f"1px solid {s.GHOST}",
                        padding_bottom="2px",
                        white_space="nowrap",
                    ),
                    href="/app",
                    _hover={},
                ),
                _hamburger_button(),
                spacing="0",
                align="center",
                gap=["16px", "16px", "16px", "34px"],
                height=["68px", "76px", "84px"],
                width="100%",
            ),
        ),
        _mobile_nav_menu(),
        position="sticky",
        top="0",
        z_index="10",
        background_color="rgba(255,254,252,.92)",
        backdrop_filter="blur(6px)",
        border_bottom=f"1px solid {s.LINE_SOFT}",
    )


# --------------------------------------------------------------------------- #
# Hero
# --------------------------------------------------------------------------- #
def _hero() -> rx.Component:
    return rx.box(
        _blob(
            "ag-float-a 9s ease-in-out infinite",
            top="-120px",
            right="-100px",
            width="420px",
            height="420px",
        ),
        _blob(
            "ag-float-b 11s ease-in-out infinite",
            bottom="-100px",
            left="-80px",
            width="320px",
            height="320px",
        ),
        wrap(
            rx.flex(
                rx.box(
                    label(State.lc["hero_eyebrow"], color=s.RUST, margin_bottom="18px"),
                    rx.heading(
                        rx.foreach(
                            State.lc_hero_lines,
                            lambda ln: rx.el.span(rx.el.span(ln), class_name="ln"),
                        ),
                        rx.el.span(
                            rx.el.span(
                                State.lc["hero_em"],
                                style={"font_style": "italic", "color": s.RUST},
                            ),
                            class_name="ln",
                        ),
                        as_="h1",
                        class_name="reveal-lines",
                        font_family=s.SERIF,
                        font_weight="400",
                        font_size=["34px", "42px", "52px"],
                        line_height="1.15",
                        margin="0",
                        max_width="600px",
                    ),
                    body(
                        State.lc["hero_sub"],
                        size="16px",
                        max_width="480px",
                        margin="22px 0 0",
                        line_height="1.7",
                        color="rgba(0,0,0,.6)",
                        custom_attrs=R,
                    ),
                    rx.flex(
                        rx.box(
                            primary_button(State.lc["hero_cta"]),
                            on_click=State.open_contact,
                            display="inline-block",
                        ),
                        rx.link(
                            rx.box(
                                State.lc["hero_ghost"],
                                color=s.INK,
                                font_family=s.SANS,
                                font_weight="500",
                                font_size="13px",
                                padding="14px 4px",
                                border_bottom=f"1px solid {s.GHOST}",
                                white_space="nowrap",
                            ),
                            href="#how",
                            _hover={},
                        ),
                        gap="22px",
                        # Stacked on mobile, side by side from md up. Catalan's
                        # longer labels already wrapped to two levels on their
                        # own; pinning the direction gives every language that
                        # same layout instead of leaving it to string length.
                        # `start` keeps them left-aligned with the copy above,
                        # which is how the wrapped version already looked.
                        direction=rx.breakpoints(initial="column", md="row"),
                        align=rx.breakpoints(initial="start", md="center"),
                        margin_top="34px",
                        wrap="wrap",
                        custom_attrs=R,
                    ),
                    flex="1 1 0",
                    min_width="0",
                ),
                rx.box(
                    corner_frame(
                        rx.image(
                            src="https://images.unsplash.com/photo-1610045944237-b06313ab8cb7?ixlib=rb-4.1.0&q=85&fm=jpg&crop=entropy&cs=srgb",  # noqa
                            width="100%",
                            height="100%",
                            object_fit="cover",
                        ),
                        aspect_ratio="4/5",
                        background=STRIPES,
                        width="100%",
                        class_name="prlx",
                        custom_attrs={**R_CLIP, "data-prlx": ".08"},
                    ),
                    flex=["1 1 auto", "1 1 auto", "0 1 42%"],
                    width="100%",
                    max_width=["360px", "420px", "none"],
                ),
                direction=rx.breakpoints(initial="column", md="row"),
                # Column on mobile, so this gap is the breathing room between
                # the CTAs and the image; row from md up, where it is the
                # copy/image column gutter instead.
                gap=["56px", "60px", "64px"],
                align="center",
                width="100%",
            ),
            padding_top=["56px", "72px", "96px"],
            padding_bottom="40px",
            position="relative",
        ),
        position="relative",
        overflow="hidden",
    )


# --------------------------------------------------------------------------- #
# Sections
# --------------------------------------------------------------------------- #
def _problem() -> rx.Component:
    return _section(
        eyebrow(State.lc["problem_eyebrow"]),
        split_heading(
            State.lc["problem_heading"],
            State.lc["problem_em"],
            size="30px",
            margin="16px 0 40px",
        ),
        _grid(
            rx.foreach(
                State.lc_problem_cards,
                lambda card: rx.box(
                    _shape(card["shape"]),
                    rx.text(
                        card["text"],
                        font_family=s.SANS,
                        font_size="13px",
                        font_weight="500",
                        line_height="1.5",
                        margin="16px 0 0",
                    ),
                    border=f"1px solid {s.LINE}",
                    border_radius="12px",
                    padding="22px 18px",
                ),
            ),
            # Target column count lands at `md` (992px), not `lg` (1280px): most
            # laptops sit between the two, and anchoring at lg silently fell back
            # to the 2-column `sm` rule (a 2x2 block instead of the intended 4x1).
            cols=rx.breakpoints(initial="1fr", sm="repeat(2,1fr)", md="repeat(4,1fr)"),
        ),
        border_top=f"1px solid {s.LINE_SOFT}",
        padding_y=["56px", "68px", "80px"],
    )


def _how() -> rx.Component:
    return _section(
        eyebrow(State.lc["how_eyebrow"]),
        split_heading(
            State.lc["how_heading"],
            State.lc["how_em"],
            max_width="520px",
            margin="16px 0 60px",
        ),
        rx.box(
            rx.box(
                position="absolute",
                top="13px",
                left="5%",
                right="5%",
                height="1px",
                background_color="rgba(0,0,0,.15)",
                display=["none", "none", "none", "block"],
            ),
            _grid(
                rx.foreach(
                    State.lc_how_steps,
                    lambda step: rx.box(
                        rx.center(
                            rx.text(
                                step["n"],
                                font_family=s.MONO,
                                font_size="11px",
                                font_weight="600",
                                color=s.RUST,
                            ),
                            width="26px",
                            height="26px",
                            border_radius="50%",
                            border=f"2px solid {s.RUST}",
                            background_color=s.SAND,
                            margin_bottom="22px",
                            position="relative",
                            z_index="1",
                        ),
                        rx.text(
                            step["title"],
                            font_family=s.SANS,
                            font_size="15px",
                            font_weight="500",
                            margin_bottom="8px",
                        ),
                        body(step["desc"], size="12.5px"),
                        position="relative",
                    ),
                ),
                cols=rx.breakpoints(initial="1fr", sm="repeat(2,1fr)", md="repeat(4,1fr)"),
                gap="24px",
            ),
            position="relative",
            width="100%",
        ),
        bg=s.SAND,
        bordered=True,
        id="how",
    )


def _personalisation() -> rx.Component:
    return _section(
        eyebrow(State.lc["pers_eyebrow"], color=s.RUST),
        split_heading(
            State.lc["pers_heading"],
            State.lc["pers_em"],
            max_width="580px",
            margin="16px 0 16px",
        ),
        body(
            State.lc["pers_sub"],
            size="14px",
            max_width="520px",
            margin="0 0 40px",
            line_height="1.7",
            custom_attrs=R,
        ),
        _grid(
            rx.foreach(
                State.lc_pers_cards,
                lambda card: rx.box(
                    label(card["label"], color=s.RUST, margin_bottom="12px"),
                    rx.text(
                        card["value"],
                        font_family=s.SANS,
                        font_size="15px",
                        font_weight="500",
                    ),
                    body(card["note"], size="12.5px", margin="8px 0 0", color=s.SUBTLE),
                    border=f"1px solid {s.LINE}",
                    border_radius="14px",
                    padding="26px 22px",
                    transition="transform .25s ease, box-shadow .25s ease",
                    _hover={
                        "transform": "translateY(-4px)",
                        "box_shadow": "0 14px 28px rgba(0,0,0,.08)",
                    },
                ),
            ),
            cols=rx.breakpoints(initial="1fr", sm="repeat(2,1fr)", md="repeat(3,1fr)"),
            gap="18px",
        ),
        id="personalisation",
    )


def _benefits() -> rx.Component:
    return _section(
        eyebrow(State.lc["ben_eyebrow"]),
        split_heading(
            State.lc["ben_heading"],
            State.lc["ben_em"],
            margin="16px 0 44px",
        ),
        _grid(
            rx.foreach(
                State.lc_ben_items,
                lambda item: rx.box(
                    _shape(item["shape"], size="22px"),
                    rx.text(
                        item["title"],
                        font_family=s.SANS,
                        font_size="13px",
                        font_weight="500",
                        margin="14px 0 6px",
                    ),
                    body(item["desc"], size="11.5px", line_height="1.5", color=s.SUBTLE),
                ),
            ),
            # Five benefit items -> five columns, so they form one clean row with
            # no trailing hole (a 6-column rule would leave one slot empty).
            cols=rx.breakpoints(initial="1fr", sm="repeat(2,1fr)", md="repeat(5,1fr)"),
            gap="14px",
        ),
        bg=s.SAND,
        bordered=True,
    )


def _use_cases() -> rx.Component:
    return _section(
        eyebrow(State.lc["uc_eyebrow"]),
        split_heading(
            State.lc["uc_heading"],
            State.lc["uc_em"],
            margin="16px 0 44px",
        ),
        _grid(
            rx.foreach(
                State.lc_uc_cards,
                lambda card: rx.box(
                    _shape(card["shape"], size="30px"),
                    rx.text(
                        card["title"],
                        font_family=s.SANS,
                        font_size="14px",
                        font_weight="500",
                        margin="16px 0 6px",
                    ),
                    body(card["desc"], size="12.5px"),
                    border=f"1px solid {s.LINE}",
                    border_radius="12px",
                    padding="24px 20px",
                ),
            ),
            cols=rx.breakpoints(initial="1fr", sm="repeat(2,1fr)", md="repeat(3,1fr)"),
            gap="14px",
        ),
        id="use-cases",
    )


def _intro(eyebrow_key: str, heading_key: str, em_key: str, sub) -> rx.Component:
    return rx.box(
        eyebrow(State.lc[eyebrow_key]),
        split_heading(State.lc[heading_key], State.lc[em_key], size="34px", margin="16px 0 20px"),
        sub,
        margin_bottom="56px",
        max_width="560px",
    )


def _tech() -> rx.Component:
    def cell(item) -> rx.Component:
        return rx.box(
            rx.hstack(
                rx.text(
                    item["n"],
                    font_family=s.MONO,
                    font_size="13px",
                    font_weight="600",
                    color=s.RUST,
                ),
                label(item["label"], color=s.RUST),
                spacing="0",
                gap="10px",
                align="center",
                margin_bottom="22px",
            ),
            rx.text(
                item["head"],
                font_family=s.SERIF,
                font_weight="400",
                font_size="22px",
                line_height="1.3",
                margin_bottom="10px",
            ),
            body(item["text"], size="13px", line_height="1.65"),
            padding=["28px 0", "28px 0", "32px 28px"],
            border_right=rx.cond(
                item["last"] == "",
                ["none", "none", f"1px solid {s.LINE}"],
                "none",
            ),
            border_bottom=rx.cond(
                item["last"] == "",
                [f"1px solid {s.LINE}", f"1px solid {s.LINE}", "none"],
                "none",
            ),
        )

    return _section(
        _intro(
            "tech_eyebrow",
            "tech_heading",
            "tech_em",
            body(
                State.lc["tech_sub"],
                size="14px",
                line_height="1.7",
                # Single line is a desktop-only conceit: on a phone nowrap just
                # ran the sentence off the side of the screen.
                white_space=["normal", "normal", "nowrap"],
                custom_attrs=R,
            ),
        ),
        _grid(
            rx.foreach(State.lc_tech_rows, cell),
            cols=rx.breakpoints(initial="1fr", md="repeat(3,1fr)"),
            gap="0",
            border_top="1px solid rgba(0,0,0,.12)",
        ),
        padding_y=["70px", "85px", "100px"],
    )


def _faq() -> rx.Component:
    def item(entry) -> rx.Component:
        return rx.box(
            rx.flex(
                rx.text(
                    entry["q"],
                    font_family=s.SERIF,
                    font_weight="400",
                    font_size=["17px", "18px", "20px"],
                    line_height="1.35",
                ),
                rx.spacer(),
                rx.text(
                    entry["sign"],
                    font_family=s.SERIF,
                    font_size="22px",
                    color=s.RUST,
                    flex="none",
                    width="24px",
                    text_align="center",
                ),
                on_click=State.toggle_faq(entry["idx"]),
                cursor="pointer",
                padding=["20px 0", "22px 0", "26px 0"],
                align="center",
                gap="32px",
                width="100%",
            ),
            rx.cond(
                entry["a"] != "",
                body(
                    entry["a"],
                    size="14px",
                    line_height="1.7",
                    color="rgba(0,0,0,.6)",
                    margin="0 0 26px",
                    max_width="640px",
                ),
            ),
            border_bottom="1px solid rgba(0,0,0,.12)",
            width="100%",
        )

    return _section(
        _intro(
            "faq_eyebrow",
            "faq_heading",
            "faq_em",
            rx.text(
                State.lc["faq_sub_before"],
                rx.text.span(
                    State.lc["faq_sub_link"],
                    on_click=State.open_contact,
                    color=s.RUST,
                    cursor="pointer",
                    text_decoration="underline",
                    text_underline_offset="2px",
                    _hover={"color": s.RUST_DARK},
                ),
                State.lc["faq_sub_after"],
                font_family=s.SANS,
                font_size="14px",
                line_height="1.7",
                color=s.MUTED,
                white_space=["normal", "normal", "nowrap"],
                margin="0",
                custom_attrs=R,
            ),
        ),
        rx.box(
            rx.foreach(State.lc_faq, item),
            border_top="1px solid rgba(0,0,0,.12)",
            width="100%",
            custom_attrs=R_STAGGER,
        ),
        bg=s.SAND,
        bordered=True,
        padding_y=["70px", "85px", "100px"],
        id="faq",
    )


def _field(component, **props) -> rx.Component:
    """A bare HTML input/textarea styled for the dark dialog.

    Deliberately `rx.el.input` / `rx.el.textarea` rather than the Radix
    `rx.input` wrappers: those carry their own light-theme text colour that
    won on specificity, rendering black text on the near-black panel.
    """
    defaults = dict(
        background_color="transparent",
        border="none",
        border_bottom="1px solid rgba(255,254,252,.25)",
        border_radius="0",
        color=s.PAPER,
        font_family=s.SANS,
        font_size="14px",
        padding="10px 2px",
        width="100%",
        outline="none",
        _placeholder={"color": "rgba(255,254,252,.55)"},
        _focus={"border_bottom_color": s.RUST, "outline": "none", "box_shadow": "none"},
        transition="border-color .2s ease",
    )
    defaults.update(props)
    return component(**defaults)


def _contact_form() -> rx.Component:
    return rx.vstack(
        _field(
            rx.el.input,
            placeholder=State.t["contact_name_ph"],
            value=State.contact_name,
            on_change=State.set_contact_name,
        ),
        _field(
            rx.el.input,
            placeholder=State.t["contact_email_ph"],
            value=State.contact_email,
            on_change=State.set_contact_email,
            type="email",
        ),
        _field(
            rx.el.textarea,
            placeholder=State.t["contact_message_ph"],
            value=State.contact_message,
            on_change=State.set_contact_message,
            rows="4",
            resize="vertical",
            line_height="1.6",
        ),
        rx.cond(
            State.contact_error != "",
            rx.text(
                State.contact_error,
                font_family=s.SANS,
                font_size="12.5px",
                color="#ff8f78",
            ),
        ),
        rx.cond(
            State.contact_sent,
            rx.hstack(
                rx.icon("check", size=16, color="#8fd19e"),
                rx.text(
                    State.t["contact_success"],
                    font_family=s.SANS,
                    font_size="13px",
                    color="#8fd19e",
                ),
                spacing="2",
                align="center",
            ),
            rx.box(
                rx.cond(
                    State.contact_sending,
                    rx.center(rx.spinner(size="2", color=s.PAPER), width="100%", padding_y="14px"),
                    rx.center(
                        rx.text(
                            State.t["contact_send"],
                            font_family=s.SANS,
                            font_size="13px",
                            font_weight="500",
                            color=s.PAPER,
                        ),
                        on_click=State.submit_contact,
                        background_color=s.RUST,
                        border_radius="9px",
                        padding="14px 26px",
                        cursor="pointer",
                        width="100%",
                        _hover={"background_color": s.RUST_DARK},
                        transition="background-color .2s ease",
                    ),
                ),
                width="100%",
            ),
        ),
        spacing="4",
        width="100%",
        max_width="440px",
        margin="0 auto",
        custom_attrs=R,
    )


def contact_dialog() -> rx.Component:
    """The contact form, as a modal opened from any 'contact' call to action."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.hstack(
                label(State.lc["cta_eyebrow"], color=s.RUST),
                rx.spacer(),
                rx.dialog.close(
                    rx.box(
                        rx.icon("x", size=18, color="rgba(255,254,252,.6)"),
                        cursor="pointer",
                        display="flex",
                        _hover={"color": s.PAPER},
                    ),
                ),
                align="center",
                width="100%",
            ),
            rx.heading(
                State.lc["cta_heading"],
                rx.text.span(State.lc["cta_em"], font_style="italic", color=s.RUST),
                ".",
                as_="h2",
                font_family=s.SERIF,
                font_weight="400",
                font_size=["26px", "28px", "30px"],
                line_height="1.2",
                color=s.PAPER,
                margin="14px 0 10px",
            ),
            body(
                State.lc["cta_sub"],
                size="13.5px",
                color="rgba(255,254,252,.6)",
                margin="0 0 26px",
            ),
            _contact_form(),
            background_color=s.INK,
            border=f"1px solid {'rgba(255,254,252,.14)'}",
            border_radius="16px",
            padding=["26px 22px", "30px 28px", "34px 34px"],
            max_width="440px",
            width="92vw",
            box_shadow="0 30px 80px -20px rgba(0,0,0,.6)",
        ),
        open=State.contact_open,
        on_open_change=State.set_contact_open,
    )


def _cta() -> rx.Component:
    return rx.box(
        wrap(
            label(
                State.lc["cta_eyebrow"],
                color="rgba(255,254,252,.5)",
                class_name="lbl-draw",
                custom_attrs=R,
                display="inline-block",
                margin_bottom="10px",
            ),
            # `max_width` alone leaves these hugging the left edge of the wrap —
            # the auto side margins are what actually centres them.
            split_heading(
                State.lc["cta_heading"],
                State.lc["cta_em"],
                size="38px",
                max_width="640px",
                color=s.PAPER,
                margin="16px auto 20px",
            ),
            body(
                State.lc["cta_sub"],
                size="14px",
                color="rgba(255,254,252,.6)",
                margin="0 auto 30px",
                max_width="440px",
                custom_attrs=R,
            ),
            rx.box(
                primary_button(State.lc["cta_button"], font_size="14px", padding="16px 32px"),
                on_click=State.open_contact,
                display="inline-block",
            ),
            custom_attrs=R_STAGGER,
            text_align="center",
        ),
        background_color=s.INK,
        color=s.PAPER,
        padding_y=["80px", "95px", "110px"],
        id="demo",
    )


def _footer() -> rx.Component:
    return rx.box(
        wrap(
            rx.flex(
                wordmark(20, font_size="13px"),
                rx.spacer(),
                label(State.lc["footer"], color=s.GHOST),
                align="center",
                gap="16px",
                direction=rx.breakpoints(initial="column", sm="row"),
                width="100%",
            ),
        ),
        padding_y="36px",
        border_top=f"1px solid {s.LINE_SOFT}",
    )


def landing() -> rx.Component:
    return rx.fragment(
        rx.script(scripts.REVEAL),
        contact_dialog(),
        rx.box(
            _nav(),
            _hero(),
            _problem(),
            _how(),
            _personalisation(),
            _benefits(),
            _use_cases(),
            _tech(),
            _faq(),
            _cta(),
            _footer(),
            width="100%",
            overflow_x="hidden",
            background_color=s.PAPER,
        ),
    )
