import time
import json
import logging
from typing import Dict, List

from dotenv import load_dotenv
import numpy as np
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

CONFIGURATIONS = [
    {
        "name": "Arnolfini Portrait",
        "image_path": "/home/afalceto/artguide/img/matrimoni_arnolfini.jpg",
        "config": {"language": "en", "speaker": "female", "duration": "short"},
    },
    {
        "name": "Guernica",
        "image_path": "/home/afalceto/artguide/img/guernica.jpeg",
        "config": {"language": "en", "speaker": "female", "duration": "short"},
    },
]

N_RUNS = 5


class ColdAPITools(APITools):
    """APITools variant that loads CLIP and Piper from scratch on every call."""

    def search_painting(self, image_base64: str) -> List[Dict]:

        db = QdrantDB()  # loads CLIP on __init__
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


def benchmark_warm(config: dict, n_runs: int) -> list[float]:
    times = []
    for i in range(n_runs):
        agent = ArtGuide(config["config"])
        start = time.perf_counter()
        agent.run(image_path=config["image_path"])
        elapsed = time.perf_counter() - start
        times.append(round(elapsed, 3))
        print(f"  [{config['name']}] Run {i + 1}/{n_runs}: {elapsed:.3f}s")
    return times


def benchmark_cold(config: dict, n_runs: int) -> list[float]:

    times = []
    for i in range(n_runs):
        agent = ArtGuide(config["config"])
        agent.api_tools = ColdAPITools(api_config["url"])
        start = time.perf_counter()
        agent.run(image_path=config["image_path"])
        elapsed = time.perf_counter() - start
        times.append(round(elapsed, 3))
        print(f"  [{config['name']}] Run {i + 1}/{n_runs}: {elapsed:.3f}s")
    return times


if __name__ == "__main__":
    load_dotenv()

    results = {}

    for cfg in CONFIGURATIONS:
        print(f"\n[WARM] Benchmarking: {cfg['name']}")
        results[cfg["name"]] = {"warm": benchmark_warm(cfg, N_RUNS)}

    for cfg in CONFIGURATIONS:
        print(f"\n[COLD] Benchmarking: {cfg['name']}")
        results[cfg["name"]]["cold"] = benchmark_cold(cfg, N_RUNS)

    print("\n--- Results ---")
    for name, runs in results.items():
        for scenario, times in runs.items():
            mean = round(sum(times) / len(times), 3)
            print(f"{name} [{scenario}]: {times}")
            print(f"  mean={mean}s  min={min(times)}s  max={max(times)}s")

    output_path = "scripts/inference_latency_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_path}")
