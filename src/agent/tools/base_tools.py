import logging
from typing import Dict, List
from requests import get

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BaseTools:
    """General tools for agent."""

    @staticmethod
    def score_meets_threshold(score: float, threshold: float) -> bool:
        return score >= threshold

    @staticmethod
    def get_top_result(results: List[Dict]) -> Dict:
        return results[0] if results else {}

    @staticmethod
    def translate_painting(painting: Dict, target_language: str) -> str:
        url = "https://translate.googleapis.com/translate_a/single"

        text = painting['title']
        params = {
            "client": "gtx", "sl": "en", "tl": target_language, "dt": "t", "q": text
        }

        try:
            response = get(url, params=params)
            response.raise_for_status()

            # Google returns nested arrays like: [[["Hola", "Hello", ...]], ...]
            translated_segments = response.json()[0]
            full_translation = "".join(segment[0] for segment in translated_segments)
            painting['title'] = full_translation
        except Exception:
            logger.info("Painting title could not be translated")

        return painting
