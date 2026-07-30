"""Design tokens for the ArtGuide frontend.

Visual language: warm paper backgrounds, near-black ink, a single rust accent,
serif display type (Newsreader) against a neutral sans (Work Sans) and
monospace eyebrow labels (IBM Plex Mono). The recurring motif is a pair of
corner brackets — ink on the top-left, rust on the bottom-right.
"""

# --- Palette ---------------------------------------------------------------
INK = "#1a1a1a"
RUST = "#c8341f"
RUST_DARK = "#a02a19"
PAPER = "#fffefc"      # primary surface
SAND = "#faf8f4"       # alternating section surface
BONE = "#f2efe9"       # page chrome / outside the frame

LINE = "rgba(0,0,0,.1)"
LINE_SOFT = "rgba(0,0,0,.06)"
MUTED = "rgba(0,0,0,.55)"
SUBTLE = "rgba(0,0,0,.5)"
FAINT = "rgba(0,0,0,.4)"
GHOST = "rgba(0,0,0,.35)"

# On dark (camera viewfinder)
DARK_GRADIENT = "linear-gradient(160deg,#2a2622,#141210)"
ON_DARK = "#ffffff"
ON_DARK_MUTED = "rgba(255,255,255,.5)"
ON_DARK_FAINT = "rgba(255,255,255,.45)"

# --- Type ------------------------------------------------------------------
SERIF = "'Newsreader', Georgia, 'Times New Roman', serif"
SANS = "'Work Sans', system-ui, -apple-system, 'Segoe UI', sans-serif"
MONO = "'IBM Plex Mono', ui-monospace, 'SF Mono', Menlo, monospace"

# --- Layout ----------------------------------------------------------------
WRAP = "1180px"
APP_WRAP = "440px"     # the app is phone-shaped even on desktop

# --- Global stylesheet -----------------------------------------------------
BASE_STYLE = {
    "background_color": PAPER,
    "color": INK,
    "font_family": SANS,
    "-webkit-font-smoothing": "antialiased",
    "::selection": {"background_color": RUST, "color": PAPER},
    "a": {"color": RUST, "text_decoration": "none"},
    "a:hover": {"color": RUST_DARK},
    # Never let a wide child scroll the whole page sideways.
    "html, body": {"overflow_x": "hidden", "max_width": "100%"},
}

# Eyebrow label: uppercase mono, wide tracking
LABEL = {
    "font_family": MONO,
    "font_size": "10px",
    "font_weight": "500",
    "letter_spacing": ".14em",
    "text_transform": "uppercase",
}
