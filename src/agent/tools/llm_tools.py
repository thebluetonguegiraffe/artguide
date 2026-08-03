import base64
import logging
import string
import time
from numpy import random
from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Union
from concurrent.futures import ThreadPoolExecutor

from src.agent.prompts import Prompts
from langchain_core.messages import HumanMessage, SystemMessage

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _describe_api_error(exc: Exception) -> str:
    """Flatten a provider exception into one loggable line, body included."""
    parts = [f"{type(exc).__name__}: {exc}"]
    status = getattr(exc, "status_code", None)
    if status is not None:
        parts.append(f"status={status}")
    body = getattr(exc, "body", None)
    if body:
        parts.append(f"body={body}")
    return " | ".join(parts)


def _is_transient(exc: Exception) -> bool:
    """Is this worth retrying? Capacity, rate limits and empty generations are."""
    status = getattr(exc, "status_code", None)
    if status in (429, 500, 502, 503):
        return True
    body = getattr(exc, "body", None) or {}
    return isinstance(body, dict) and body.get("code") == "json_validate_failed"


class ChatArtworkInfo(BaseModel):
    # Every field defaults to None: the vision model is asked for free-form JSON and
    # legitimately omits keys it cannot determine, which would otherwise fail parsing.
    title: Optional[str] = None
    artist: Optional[str] = None
    year: Optional[Union[str, int]] = None  # models return the year as a bare number
    museum: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self):
        return {
            "title": self.title,
            "artist": self.artist,
            "year": str(self.year) if self.year is not None else None,
            "museum": self.museum,
            "description": self.description.replace("*", "") if self.description else None,
        }


class LLMTools:

    LANGUAGE_MAPPER = {"ca": "català", "es": "español", "en": "english"}

    MODEL_ATTEMPTS = 2
    MODEL_RETRY_WAIT = 2  # seconds, multiplied by the attempt number

    def __init__(
        self,
        description_model,
        first_vision_model,
        second_vision_model,
        judge_model,
        structured_output_method: str = "json_mode",
    ):
        self.description_model = description_model
        self.first_vision_model = first_vision_model or description_model
        self.second_vision_model = second_vision_model or description_model
        self.judge_model = judge_model or description_model

        self.prompts = Prompts
        self.structured_output_method = structured_output_method

    def identify_artwork(
        self, image_path: str, language: str, n_words: int, candidates: List[Dict] = None
    ) -> Dict:
        """Identifies painting via two independent blind LLM opinions plus CLIP's
        own candidate (when available), arbitrated by a judge call over anonymized
        options. Neither blind model ever sees the other's answer or CLIP's hint --
        that anchoring is exactly what we're avoiding here."""

        first_model_inference = self.first_vision_model.with_structured_output(
            ChatArtworkInfo, method=self.structured_output_method
        )
        second_model_inference = self.second_vision_model.with_structured_output(
            ChatArtworkInfo, method=self.structured_output_method
        )

        with open(image_path, "rb") as img:
            image_b64 = base64.b64encode(img.read()).decode("utf-8")

        image_content = {
            "type": "image_url",
            "image_url": {"url": "data:image/jpeg;base64," + image_b64},
        }

        logger.info(f"Deep analysis on image: {image_path} ({len(image_b64) / 1e6:.2f}MB base64)")

        blind_prompt = self.prompts.ART_IDENTIFICATION_PROMPT.format(
            language=self.LANGUAGE_MAPPER[language],
            n_words=n_words,
        )
        blind_messages = [
            SystemMessage(content=self.prompts.SYSTEM_GUIDELINES),
            HumanMessage(content=[{"type": "text", "text": blind_prompt}, image_content]),
        ]

        # The two blind calls are independent network requests -- run them
        # concurrently so wall-clock cost is bounded by the slower one, not the sum.
        with ThreadPoolExecutor(max_workers=2) as executor:
            first_future = executor.submit(
                self._invoke_blind, blind_messages, first_model_inference, "first_vision_model"
            )
            second_future = executor.submit(
                self._invoke_blind, blind_messages, second_model_inference, "second_vision_model"
            )
            first_result = first_future.result()
            second_result = second_future.result()

        logger.info(
            f"Blind opinions -- "
            f"first: title={first_result['title']!r} artist={first_result['artist']!r} | "
            f"second: title={second_result['title']!r} artist={second_result['artist']!r}"
        )

        options = [first_result, second_result]
        random.shuffle(options)
        options_block = "\n".join(
            f"Option {letter}: title={opt['title']!r}, artist={opt.get('artist', '')!r}"
            for letter, opt in zip(string.ascii_uppercase, options)
        )

        clip_evidence_block = ""
        if candidates:
            lines = []
            for candidate in candidates:
                if not candidate.get("title"):
                    continue
                artist_clause = (
                    f", artist: {candidate['artist']!r}" if candidate.get("artist") else ""
                )
                score = candidate.get("score")
                score_clause = (
                    f", visual similarity score: {score:.3f}" if score is not None else ""
                )
                lines.append(f"  - title: {candidate['title']!r}{artist_clause}{score_clause}")

            if lines:
                clip_evidence_block = (
                    "Additional evidence -- visual similarity search against the indexed "
                    "artwork database (vector-similarity matches, not model opinions):\n"
                    + "\n".join(lines)
                    + "\n\n"
                )
                logger.info(
                    f"Including {len(lines)} CLIP evidence candidate(s) in judge prompt: {lines}"
                )

        judge_prompt = self.prompts.ART_IDENTIFICATION_JUDGE_PROMPT.format(
            language=self.LANGUAGE_MAPPER[language],
            n_words=n_words,
            options_block=options_block,
            clip_evidence_block=clip_evidence_block,
        )
        judge_messages = [
            SystemMessage(content=self.prompts.SYSTEM_GUIDELINES),
            HumanMessage(content=[{"type": "text", "text": judge_prompt}, image_content]),
        ]

        for attempt in range(1, self.MODEL_ATTEMPTS + 1):
            try:
                response = first_model_inference.invoke(judge_messages)
                break
            except Exception as exc:
                logger.error(
                    f"Judge identification failed "
                    f"(attempt {attempt}/{self.MODEL_ATTEMPTS}): {_describe_api_error(exc)}"
                )
                if attempt == self.MODEL_ATTEMPTS or not _is_transient(exc):
                    raise
                time.sleep(self.MODEL_RETRY_WAIT * attempt)

        result = response.to_dict()
        logger.info(f"Identified: title={result['title']!r} artist={result['artist']!r}")
        return result

    def enrich_painting(self, title: str, language: str, n_words: int) -> str:
        """Generates painting description and enriches painting info"""

        logger.info(f"Generating description: {title}")
        llm_artwork_info = self.description_model.with_structured_output(ChatArtworkInfo)

        prompt = self.prompts.DESCRIPTION_GENERATION.format(
            language=language, n_words=n_words, title=title
        )

        response = llm_artwork_info.invoke(
            [SystemMessage(content=self.prompts.SYSTEM_GUIDELINES), HumanMessage(content=prompt)]
        )

        return response.to_dict()

    def _invoke_blind(self, blind_messages: List, model_inference: Any, model_label: str) -> Dict:
        for attempt in range(1, self.MODEL_ATTEMPTS + 1):
            try:
                response = model_inference.invoke(blind_messages)
                return response.to_dict()
            except Exception as exc:
                logger.error(
                    f"{model_label} identification failed "
                    f"(attempt {attempt}/{self.MODEL_ATTEMPTS}): {_describe_api_error(exc)}"
                )
                if attempt == self.MODEL_ATTEMPTS or not _is_transient(exc):
                    raise
                time.sleep(self.MODEL_RETRY_WAIT * attempt)
