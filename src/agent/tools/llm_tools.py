import base64
import logging
import time
from typing import Dict, Optional, Union

from pydantic import BaseModel

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

    LANGUAGE_MAPPER = {
        "ca": "català",
        "es": "español",
        "en": "english"
    }

    VISION_ATTEMPTS = 2
    VISION_RETRY_WAIT = 2  # seconds, multiplied by the attempt number

    def __init__(self, llm, vision_llm=None):
        self.llm = llm
        self.vision_llm = vision_llm or llm
        self.prompts = Prompts

    def identify_artwork(self, image_path: str, language: str, n_words: int) -> Dict:
        """Identifies painting using LLM"""

        # `json_mode` rather than the default `json_schema`: the vision models available
        # on Groq support neither json_schema nor reliable tool calling, so the schema is
        # spelled out in the prompt and validated by ChatArtworkInfo on the way out.
        llm_artwork_info = self.vision_llm.with_structured_output(
            ChatArtworkInfo, method="json_mode"
        )
        with open(image_path, "rb") as img:
            image_b64 = base64.b64encode(img.read()).decode("utf-8")

        logger.info(
            f"Deep analysis on image: {image_path} "
            f"({len(image_b64) / 1e6:.2f}MB base64, model={getattr(self.vision_llm, 'model_name', '?')})"  # noqa
        )
        prompt = self.prompts.ART_IDENTIFICATION_PROMPT.format(
            language=self.LANGUAGE_MAPPER[language],
            n_words=n_words
        )
        messages = [
            SystemMessage(content=self.prompts.SYSTEM_GUIDELINES),
            HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/jpeg;base64," + image_b64},
                    },
                ]
            ),
        ]

        # Groq serves this model on shared capacity and intermittently answers 503
        # ("over capacity") or drops an empty generation. Both are transient, and
        # without a retry a single flake surfaces as "unknown painting".
        for attempt in range(1, self.VISION_ATTEMPTS + 1):
            try:
                response = llm_artwork_info.invoke(messages)
                break
            except Exception as exc:
                # The provider's own explanation lives in the response body, which the
                # exception's str() truncates away -- without it a failure here is an
                # unattributable "unknown painting" in the UI.
                logger.error(
                    f"Vision identification failed "
                    f"(attempt {attempt}/{self.VISION_ATTEMPTS}): {_describe_api_error(exc)}"
                )
                if attempt == self.VISION_ATTEMPTS or not _is_transient(exc):
                    raise
                time.sleep(self.VISION_RETRY_WAIT * attempt)

        result = response.to_dict()
        logger.info(f"Identified: title={result['title']!r} artist={result['artist']!r}")
        return result

    def enrich_painting(self, title: str, language: str, n_words: int) -> str:
        """Generates painting description and enriches painting info"""

        logger.info(f"Generating description: {title}")
        llm_artwork_info = self.llm.with_structured_output(ChatArtworkInfo)

        prompt = self.prompts.DESCRIPTION_GENERATION.format(
            language=language,
            n_words=n_words,
            title=title
        )

        response = llm_artwork_info.invoke(
            [SystemMessage(content=self.prompts.SYSTEM_GUIDELINES), HumanMessage(content=prompt)]
        )

        return response.to_dict()
