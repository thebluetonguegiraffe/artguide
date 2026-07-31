"""Application state: configuration, landing copy and the recognition pipeline."""
import asyncio
import base64
import binascii
import io
import logging
import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import reflex as rx
from PIL import Image, ImageOps
from scipy.io import wavfile

# iPhones hand over HEIC, which Pillow cannot open on its own. Optional so a
# missing wheel degrades to "HEIC uploads fail" rather than breaking startup.
try:
    from pillow_heif import register_heif_opener

    register_heif_opener()
except ImportError:
    pass

from artguide_app.translations import TEXT_TRANSLATIONS as tt
from artguide_app.landing_texts import LANDING, WAITING_PHRASES
from artguide_app.contact import send_contact_email

# --- Make the parent project importable (src.agent, config, .env) -----------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env")
except Exception:  # pragma: no cover - dotenv optional
    pass

LANGUAGES = ["es", "ca", "en"]

# The agent's tools log through `logging`, which reaches stderr and therefore the
# container logs. Anything printed to stdout does not: it sits in Python's block
# buffer until the process exits, so pipeline failures were invisible in practice.
logging.basicConfig(  # no-op if the root logger is already configured
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger("artguide.app")

# Scalar (plain string) landing keys exposed as one dict var.
_SCALAR_KEYS = [
    "nav_cta", "open_app", "hero_eyebrow", "hero_em", "hero_sub", "hero_cta",
    "hero_ghost", "hero_frame",
    "problem_eyebrow", "problem_heading", "problem_em",
    "how_eyebrow", "how_heading", "how_em",
    "pers_eyebrow", "pers_heading", "pers_em", "pers_sub",
    "ben_eyebrow", "ben_heading", "ben_em",
    "uc_eyebrow", "uc_heading", "uc_em",
    "tech_eyebrow", "tech_heading", "tech_em", "tech_sub",
    "faq_eyebrow", "faq_heading", "faq_em",
    "faq_sub_before", "faq_sub_link", "faq_sub_after",
    "cta_eyebrow", "cta_heading", "cta_em", "cta_sub", "cta_button", "footer",
]

# Decorative shapes cycled through the benefit / problem grids.
_SHAPES = ["bracket_tl", "circle", "leaf", "dashed", "bracket_br"]


def _samples_to_wav_data_uri(samples, sr: int) -> str:
    """Convert float32 PCM samples returned by the API into a base64 wav data URI."""
    arr = np.asarray(samples, dtype=np.float32)
    byte_io = io.BytesIO()
    wavfile.write(byte_io, sr, arr)
    return f"data:audio/wav;base64,{base64.b64encode(byte_io.getvalue()).decode()}"


class State(rx.State):
    # ---- Configuration ----------------------------------------------------
    language: str = "es"
    speaker: str = "female"
    duration: str = "short"
    settings_open: bool = False
    mobile_nav_open: bool = False

    # ---- Landing ----------------------------------------------------------
    faq_open: int = 0

    # ---- Contact form -------------------------------------------------------
    contact_name: str = ""
    contact_email: str = ""
    contact_message: str = ""
    contact_sending: bool = False
    contact_sent: bool = False
    contact_error: str = ""
    contact_open: bool = False

    # ---- App pipeline -----------------------------------------------------
    # stage: "idle" | "analyzing" | "result" | "error"
    stage: str = "idle"
    camera_on: bool = False
    camera_error_kind: str = ""   # "" = fine; else the DOMException name

    # Upload runs before `stage` leaves "idle", so without these the UI sat on
    # the viewfinder with no sign anything was happening -- on a phone that is
    # several seconds of a multi-megabyte POST looking like a dead button.
    uploading: bool = False
    upload_pct: int = 0

    shot: str = ""            # data URI of the captured/uploaded photo
    title: str = ""
    artist: str = ""
    year: str = ""
    museum: str = ""
    description: str = ""
    audio_src: str = ""
    confidence: str = ""      # e.g. "98" (empty when the deep search answered)
    audio_generating: bool = False
    audio_error: bool = False
    description_error: bool = False

    _temp_path: str = ""

    # ======================= Localised app strings =========================
    @rx.var
    def t(self) -> dict[str, str]:
        return tt[self.language]

    # ======================= Landing copy vars =============================
    @rx.var
    def lc(self) -> dict[str, str]:
        src = LANDING[self.language]
        return {k: src[k] for k in _SCALAR_KEYS}

    @rx.var
    def lc_nav(self) -> list[dict[str, str]]:
        anchors = ["#how", "#personalisation", "#use-cases", "#faq"]
        return [
            {"text": t, "href": h}
            for t, h in zip(LANDING[self.language]["nav"], anchors)
        ]

    @rx.var
    def lc_problem_cards(self) -> list[dict[str, str]]:
        return [
            {"text": t, "shape": _SHAPES[i % len(_SHAPES)]}
            for i, t in enumerate(LANDING[self.language]["problem_cards"])
        ]

    @rx.var
    def lc_how_steps(self) -> list[dict[str, str]]:
        return [
            {"n": f"0{i + 1}", "title": title, "desc": desc}
            for i, (title, desc) in enumerate(LANDING[self.language]["how_steps"])
        ]

    @rx.var
    def lc_pers_cards(self) -> list[dict[str, str]]:
        return [
            {"label": lab, "value": val, "note": note}
            for lab, val, note in LANDING[self.language]["pers_cards"]
        ]

    @rx.var
    def lc_ben_items(self) -> list[dict[str, str]]:
        return [
            {"title": t, "desc": d, "shape": _SHAPES[i % len(_SHAPES)]}
            for i, (t, d) in enumerate(LANDING[self.language]["ben_items"])
        ]

    @rx.var
    def lc_uc_cards(self) -> list[dict[str, str]]:
        return [
            {"title": t, "desc": d, "shape": _SHAPES[i % len(_SHAPES)]}
            for i, (t, d) in enumerate(LANDING[self.language]["uc_cards"])
        ]

    @rx.var
    def lc_hero_lines(self) -> list[str]:
        return LANDING[self.language]["hero_lines"]

    @rx.var
    def waiting_phrases(self) -> list[dict[str, str]]:
        """Rotating lines on the desktop side panel, each with its own delay."""
        return [
            {"before": b, "em": em, "after": a, "delay": f"{i * 4}s"}
            for i, (b, em, a) in enumerate(WAITING_PHRASES[self.language])
        ]

    @rx.var
    def lc_tech_rows(self) -> list[dict[str, str]]:
        rows = LANDING[self.language]["tech_rows"]
        return [
            {
                "n": f"0{i + 1}",
                "label": lab,
                "head": head,
                "text": txt,
                "last": "1" if i == len(rows) - 1 else "",
            }
            for i, (lab, head, txt) in enumerate(rows)
        ]

    @rx.var
    def lc_faq(self) -> list[dict[str, str]]:
        out = []
        for i, (q, a) in enumerate(LANDING[self.language]["faq"]):
            is_open = i == self.faq_open
            out.append(
                {
                    "q": q,
                    "a": a if is_open else "",
                    "sign": "–" if is_open else "+",
                    "idx": str(i),
                }
            )
        return out

    # ---- Settings labels --------------------------------------------------
    @rx.var
    def speaker_labels(self) -> list[str]:
        return [tt[self.language]["female_speaker"], tt[self.language]["male_speaker"]]

    @rx.var
    def current_speaker_label(self) -> str:
        key = "female_speaker" if self.speaker == "female" else "male_speaker"
        return tt[self.language][key]

    @rx.var
    def duration_labels(self) -> list[str]:
        d = tt[self.language]
        return [d["short_audio"], d["medium_audio"], d["long_audio"]]

    @rx.var
    def current_duration_label(self) -> str:
        key = {"short": "short_audio", "medium": "medium_audio", "long": "long_audio"}
        return tt[self.language][key[self.duration]]

    # ======================= Events ========================================
    @rx.event
    def set_language(self, lang: str):
        if lang in tt:
            self.language = lang

    @rx.event
    def toggle_faq(self, idx: str):
        i = int(idx)
        self.faq_open = -1 if self.faq_open == i else i

    @rx.event
    def toggle_settings(self):
        self.settings_open = not self.settings_open

    @rx.event
    def close_settings(self):
        self.settings_open = False

    @rx.event
    def toggle_mobile_nav(self):
        self.mobile_nav_open = not self.mobile_nav_open

    @rx.event
    def close_mobile_nav(self):
        self.mobile_nav_open = False

    @rx.event
    def set_duration(self, value: str):
        if value in ("short", "medium", "long"):
            self.duration = value

    @rx.event
    def set_speaker(self, value: str):
        if value in ("female", "male"):
            self.speaker = value

    @rx.event
    def set_speaker_from_label(self, label: str):
        for lang in tt:
            if label == tt[lang]["female_speaker"]:
                self.speaker = "female"
                return
            if label == tt[lang]["male_speaker"]:
                self.speaker = "male"
                return

    @rx.event
    def set_duration_from_label(self, label: str):
        mapping = {}
        for lang in tt:
            mapping[tt[lang]["short_audio"]] = "short"
            mapping[tt[lang]["medium_audio"]] = "medium"
            mapping[tt[lang]["long_audio"]] = "long"
        if label in mapping:
            self.duration = mapping[label]

    # ---- Reset / camera ---------------------------------------------------
    def _clear(self):
        self.stage = "idle"
        self.uploading = False
        self.upload_pct = 0
        self.shot = ""
        self.title = ""
        self.artist = ""
        self.year = ""
        self.museum = ""
        self.description = ""
        self.audio_src = ""
        self.confidence = ""
        self.audio_generating = False
        self.audio_error = False
        self.description_error = False

    @rx.event
    def restart(self):
        """Back to the viewfinder."""
        self._clear()
        self.camera_on = False

    @rx.event
    def set_camera_on(self, on: bool):
        self.camera_on = on
        if on:
            self.camera_error_kind = ""

    @rx.event
    def camera_started(self, reason: str):
        """Callback from getUserMedia: "" means the stream is live.

        "Skip" comes from an auto-start attempt on a hidden (desktop)
        viewfinder — ignore it rather than surfacing a spurious error.
        """
        if reason == "Skip":
            return
        self.camera_on = reason == ""
        self.camera_error_kind = reason

    @rx.var
    def camera_error(self) -> bool:
        return self.camera_error_kind != ""

    @rx.var
    def camera_message(self) -> str:
        """Actionable explanation for whichever way the camera failed."""
        texts = tt[self.language]
        if self.camera_error_kind == "":
            return ""
        # `NotSupported` means navigator.mediaDevices was missing entirely, which
        # is what happens on an insecure origin (e.g. reaching the dev server by
        # LAN IP over plain http from a phone) — the browser never even prompts.
        if self.camera_error_kind == "NotSupported":
            return texts["camera_insecure"]
        if self.camera_error_kind in ("NotAllowedError", "SecurityError"):
            return texts["camera_denied"]
        if self.camera_error_kind in ("NotFoundError", "OverconstrainedError"):
            return texts["camera_missing"]
        return texts["camera_blocked"]

    # ---- Entry points -----------------------------------------------------
    @rx.event
    def on_upload_progress(self, progress: dict):
        """Drives the "uploading" affordance while the POST is in flight."""
        self.uploading = True
        self.upload_pct = int(float(progress.get("progress", 0)) * 100)

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        self.uploading = False
        self.upload_pct = 0
        if not files:
            return
        data = await files[0].read()
        return State._begin(self, data)

    @rx.event
    def capture_photo(self, data_url: str):
        """Receive a still frame captured from the live viewfinder."""
        if not data_url or "," not in data_url:
            return
        try:
            data = base64.b64decode(data_url.split(",", 1)[1])
        except (binascii.Error, ValueError):
            return
        return State._begin(self, data)

    @staticmethod
    def _to_jpeg(data: bytes, max_side: int | None = None) -> bytes:
        """Normalise whatever the phone handed us into a plain JPEG.

        Uploads are not necessarily JPEG or PNG: an iPhone's library serves
        HEIC, and Android pickers produce webp. Both the agent and the browser
        preview want something ordinary, so everything is decoded and re-encoded
        here rather than each caller guessing at the format.

        `exif_transpose` matters on phones specifically: cameras record the
        orientation as EXIF metadata instead of rotating the pixels, so a photo
        taken sideways reaches the agent sideways unless it is applied.

        Returns the original bytes untouched if Pillow cannot decode them --
        better to let the agent try than to fail outright here.
        """
        try:
            img = Image.open(io.BytesIO(data))
            img = ImageOps.exif_transpose(img)
            if max_side:
                img.thumbnail((max_side, max_side))
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            return buf.getvalue()
        except (OSError, ValueError, Image.DecompressionBombError):
            return data

    def _begin(self, data: bytes):
        """Shared setup for both entry points, then hand off to the agent."""
        self._clear()
        # The temp file is what the agent reads, so it gets the full-size image;
        # `shot` only has to fill a preview box, and it travels to the browser
        # base64-encoded inside a websocket delta, so it gets a small one.
        full = State._to_jpeg(data)
        self.shot = (
            "data:image/jpeg;base64,"
            + base64.b64encode(State._to_jpeg(data, max_side=1280)).decode()
        )
        self.stage = "analyzing"
        self.camera_on = False
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(full)
            self._temp_path = tmp.name
        return State.run_agent

    # ---- Pipeline ---------------------------------------------------------
    @rx.event(background=True)
    async def run_agent(self):
        async with self:
            tmp_path = self._temp_path
            config = {
                "language": self.language,
                "speaker": self.speaker,
                "duration": self.duration,
            }
        if not tmp_path:
            return

        try:
            from src.agent.artguide_agent import ArtGuide

            agent = ArtGuide(config=config)
            gen = agent.run_streaming(tmp_path)

            def _next(g):
                try:
                    return next(g)
                except StopIteration:
                    return None

            while True:
                update = await asyncio.to_thread(_next, gen)
                if update is None:
                    break
                st = update["state"]

                if st.get("status") == "error":
                    async with self:
                        self.stage = "error"
                        self.audio_generating = False
                    continue

                if "sr" in st:
                    audio_uri = _samples_to_wav_data_uri(st["samples"], st["sr"])
                    async with self:
                        self.audio_src = audio_uri
                        self.audio_generating = False
                        self.audio_error = False
                elif "top_result" in st and st["top_result"].get("title"):
                    # `top_result` grows richer at each step (identification, then
                    # description) — pick up whatever's newly present rather than
                    # waiting for the final "sr" event, so a later TTS failure
                    # doesn't strand an already-generated description unshown.
                    top = st["top_result"]
                    score = top.get("score")
                    description = top.get("description")
                    async with self:
                        self.title = str(top.get("title", ""))
                        self.artist = str(top.get("artist", "") or "")
                        self.year = str(top.get("year", "") or "")
                        self.museum = str(top.get("museum", "") or "")
                        if isinstance(score, (int, float)):
                            self.confidence = str(round(float(score) * 100))
                        self.stage = "result"
                        if description:
                            self.description = str(description)
                            self.description_error = False
                            self.audio_generating = True

        except Exception as exc:
            # exc_info so the traceback names the failing node, and the stage flags so
            # the log line says how far the pipeline got before dying.
            logger.error(
                f"Pipeline failed (title={self.title!r}, "
                f"has_description={bool(self.description)}): {exc}",
                exc_info=True,
            )
            async with self:
                if self.description:
                    # Identification and description both succeeded — only the
                    # audio synthesis step failed, so keep showing the text.
                    self.audio_error = True
                    self.audio_generating = False
                elif self.title:
                    # The artwork was identified but the description call failed.
                    self.description_error = True
                    self.audio_generating = False
                else:
                    # Never got a usable identification at all.
                    self.stage = "error"
                    self.audio_generating = False
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

    # ---- Contact form -------------------------------------------------------
    @rx.event
    def open_contact(self):
        self.contact_open = True
        self.mobile_nav_open = False
        # A fresh dialog should not show the previous submission's outcome.
        self.contact_sent = False
        self.contact_error = ""

    @rx.event
    def set_contact_open(self, is_open: bool):
        self.contact_open = is_open

    @rx.event
    def set_contact_name(self, value: str):
        self.contact_name = value

    @rx.event
    def set_contact_email(self, value: str):
        self.contact_email = value

    @rx.event
    def set_contact_message(self, value: str):
        self.contact_message = value

    @rx.event(background=True)
    async def submit_contact(self):
        async with self:
            name = self.contact_name.strip()
            email = self.contact_email.strip()
            message = self.contact_message.strip()
            texts = tt[self.language]
            self.contact_error = ""
            self.contact_sent = False

        if not (name and email and message):
            async with self:
                self.contact_error = texts["contact_error_required"]
            return
        if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            async with self:
                self.contact_error = texts["contact_error_email"]
            return

        async with self:
            self.contact_sending = True
        try:
            ok = await asyncio.to_thread(send_contact_email, name, email, message)
        except Exception:
            ok = False

        async with self:
            self.contact_sending = False
            if ok:
                self.contact_sent = True
                self.contact_name = ""
                self.contact_email = ""
                self.contact_message = ""
            else:
                self.contact_error = texts["contact_error_generic"]
