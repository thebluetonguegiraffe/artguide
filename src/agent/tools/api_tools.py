import os
import logging
from typing import Dict, List

import numpy as np
from requests import post


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


class APITools:

    def __init__(self, base_url: str):
        self.base_url = base_url

    @staticmethod
    def _parse(response, endpoint: str):
        """Decode a response, reporting the real HTTP failure instead of a JSON error.

        A down API answers with an HTML error page from the proxy; calling .json() on it
        blindly raises `Expecting value: line 1 column 1`, which says nothing about the
        outage that actually caused it.
        """
        if not response.ok:
            logger.error(
                f"{endpoint} failed: HTTP {response.status_code} — {response.text[:200]!r}"
            )
            response.raise_for_status()
        try:
            return response.json()
        except ValueError:
            logger.error(
                f"{endpoint} returned non-JSON (HTTP {response.status_code}): "
                f"{response.text[:200]!r}"
            )
            raise

    def _get_headers(self) -> Dict:
        return {
            "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
            "Content-Type": "application/json",
        }

    def search_painting(self, image_path: str) -> List[Dict]:
        """Searches for a painting in the Qdrant DB."""

        params = {"image_data": image_path}
        response = post(
            url=f"{self.base_url}/search",
            headers=self._get_headers(),
            json=params,
        )
        results = self._parse(response, "search_painting")
        top_score = results[0].get("score") if results else None
        logger.info(f"Vector search returned {len(results)} results, top score={top_score}")
        logger.info(f"Results are: {' - '.join(str(r) for r in results)}.")

        return results

    def synthesize_speech(self, text: str, speaker: str, language: str) -> Dict:
        """Perform voice synthesis"""

        logger.info(f"Generating audio for text length: {len(text)}")

        params = {"text": text, "speaker": speaker, "language": language}

        response = post(
            url=f"{self.base_url}/synthesize",
            headers=self._get_headers(),
            json=params,
        )
        results = self._parse(response, "synthesize_speech")

        return {"samples": np.array(results["samples"], dtype=np.float32), "sr": results["sr"]}
