import time
import json
import logging
import threading
import numpy as np
import psutil
import os
from typing import Dict, List
from dotenv import load_dotenv
from src.services.qdrant_db import QdrantDB
from src.agent.tools.api_tools import APITools
from src.agent.artguide_agent import ArtGuide
from src.services.piper_speaker import PIPER_VOICE_MAPPER, PiperSpeaker
from config import api_config

logging.getLogger("src.agent").setLevel(logging.WARNING)
logging.getLogger("src.services.qdrant_db").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("src.services.piper_speaker").setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING)

SAMPLE_INTERVAL = 0.5  # seconds between memory samples

CONFIG = {
    "name": "Arnolfini Portrait",
    "image_path": "/home/afalceto/artguide/img/matrimoni_arnolfini.jpg",
    "config": {"language": "en", "speaker": "female", "duration": "short"},
}


class ColdAPITools(APITools):
    def search_painting(self, image_base64: str) -> List[Dict]:
        db = QdrantDB()
        results = db.search(image_base64)
        for r in results:
            r.setdefault("image_url", None)
            r.setdefault("url", None)
        return results

    def synthesize_speech(self, text: str, speaker: str, language: str) -> Dict:
        piper_model, piper_speaker = PIPER_VOICE_MAPPER[(language, speaker)]
        tts = PiperSpeaker(model=piper_model, speaker=piper_speaker)
        audio_array, sample_rate = tts.synthesize(text)
        del tts
        return {"samples": np.array(audio_array, dtype=np.float32), "sr": sample_rate}


class MemorySampler:
    """Samples RSS memory of the current process in a background thread."""

    def __init__(self, interval: float = SAMPLE_INTERVAL):
        self.interval = interval
        self.process = psutil.Process(os.getpid())
        self.samples = []       # list of (relative_time, rss_mb)
        self.events = []        # list of (relative_time, label)
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._start_time = None

    def start(self):
        self._start_time = time.perf_counter()
        self._thread.start()

    def mark(self, label: str):
        t = round(time.perf_counter() - self._start_time, 3)
        self.events.append((t, label))
        print(f"  [mark] {label} @ {t}s")

    def stop(self):
        self._stop.set()
        self._thread.join()

    def _run(self):
        while not self._stop.is_set():
            t = round(time.perf_counter() - self._start_time, 3)
            rss_mb = round(self.process.memory_info().rss / 1024 / 1024, 2)
            self.samples.append((t, rss_mb))
            time.sleep(self.interval)


def run_warm(config: dict, sampler: MemorySampler):
    sampler.mark("agent start (warm)")
    agent = ArtGuide(config["config"])
    agent.run(image_path=config["image_path"])
    sampler.mark("agent end (warm)")


def run_cold(config: dict, sampler: MemorySampler):
    sampler.mark("agent start (cold)")
    agent = ArtGuide(config["config"])
    agent.api_tools = ColdAPITools(api_config["url"])
    agent.run(image_path=config["image_path"])
    sampler.mark("agent end (cold)")


if __name__ == "__main__":
    load_dotenv()

    print("\n--- Warm run ---")
    sampler_warm = MemorySampler()
    sampler_warm.start()
    time.sleep(1)  # baseline
    run_warm(CONFIG, sampler_warm)
    time.sleep(1)  # cooldown
    sampler_warm.stop()

    print("\n--- Cold run ---")
    sampler_cold = MemorySampler()
    sampler_cold.start()
    time.sleep(1)  # baseline
    run_cold(CONFIG, sampler_cold)
    time.sleep(1)  # cooldown
    sampler_cold.stop()

    output = {
        "warm": {
            "samples": sampler_warm.samples,
            "events": sampler_warm.events,
        },
        "cold": {
            "samples": sampler_cold.samples,
            "events": sampler_cold.events,
        },
    }

    output_path = "scripts/memory_results.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {output_path}")
