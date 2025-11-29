import base64
import logging
from typing import Dict, Optional

from pydantic import BaseModel

from src.agent.prompts import Prompts
from langchain_core.messages import HumanMessage, SystemMessage

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ChatArtworkInfo(BaseModel):
    title: Optional[str]
    artist: Optional[str]
    year: Optional[str]
    museum: Optional[str]
    description: Optional[str]

    def to_dict(self):
        return {
            "title": self.title,
            "artist": self.artist,
            "year": self.year,
            "museum": self.museum,
            "description": self.description.replace("*", "") if self.description else None,
        }


class LLMTools:

    LANGUAGE_MAPPER = {
        "ca": "català",
        "es": "español",
        "en": "english"
    }

    def __init__(self, llm):
        self.llm = llm
        self.prompts = Prompts

    def identify_artwork(self, image_path: str, language: str, n_words: int) -> Dict:
        """Identifies painting using LLM"""

        llm_artwork_info = self.llm.with_structured_output(ChatArtworkInfo)
        with open(image_path, "rb") as img:
            logger.info(f"Deep analysis on image: {image_path}")
            prompt = self.prompts.ART_IDENTIFICATION_PROMPT.format(
                language=self.LANGUAGE_MAPPER[language],
                n_words=n_words
            )
            response = llm_artwork_info.invoke(
                [
                    SystemMessage(content=self.prompts.SYSTEM_GUIDELINES),
                    HumanMessage(
                        content=[
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": "data:image/jpeg;base64,"
                                    + base64.b64encode(img.read()).decode("utf-8")
                                },
                            },
                        ]
                    ),
                ]
            )

        return response.to_dict()

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
