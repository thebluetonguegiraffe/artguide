import base64
import json
import logging
from typing import Dict, List

from dotenv import load_dotenv

from benchmarks.models.generate_dataset import load_eval_set
from benchmarks.models.utils import print_threshold_table, sweep_thresholds, THRESHOLDS

from src.services.qdrant_db import QdrantDB

logging.getLogger("src.services.qdrant_db").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)
logging.getLogger("qdrant_client").setLevel(logging.ERROR)
logging.basicConfig(level=logging.ERROR)

CACHE_DIR_FAMOUS = "benchmarks/models/bench_cache/famous"
CACHE_DIR_RANDOM = "benchmarks/models/bench_cache/random"


def run_raw_searches(eval_set: List[Dict], db: QdrantDB) -> List[Dict]:
    """Run the CLIP/Qdrant search once per image and cache the raw top-1 outcome.

    Sweeping thresholds only changes the accept/reject decision on a fixed score, not
    the search itself, so the expensive part (embedding + vector search) is done once
    per image and reused for every threshold in THRESHOLDS.
    """
    raw = []
    for i, item in enumerate(eval_set, 1):
        with open(item["image_path"], "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("utf-8")

        try:
            results = db.search(image_b64)
        except Exception as exc:
            print(f"  [{i}/{len(eval_set)}] search failed for {item['title']!r}: {exc}")
            continue

        top1 = results[0] if results else {"title": None, "score": 0.0}
        raw.append({"expected": item["title"], "top1_title": top1["title"], "score": top1["score"]})
        print(
            f"  [{i}/{len(eval_set)}] expected={item['title']!r} "
            f"top1={top1['title']!r} score={top1['score']:.3f}"
        )
    return raw


if __name__ == "__main__":
    load_dotenv()
    db = QdrantDB()

    eval_set_random = load_eval_set(CACHE_DIR_RANDOM)
    print(f"  {len(eval_set_random)} usable images cached at {CACHE_DIR_RANDOM}\n")

    print("Running CLIP/Qdrant search once per image...")
    raw_results = run_raw_searches(eval_set_random, db)

    print("\n--- Threshold comparison ---")
    table = sweep_thresholds(raw_results, THRESHOLDS)
    print_threshold_table(table)

    output_path = "benchmarks/models/benchmark_threshold_random.json"
    with open(output_path, "w") as f:
        json.dump({"raw": raw_results, "thresholds": table}, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {output_path}")

    eval_set_famous = load_eval_set(CACHE_DIR_FAMOUS)
    print(f"  {len(eval_set_famous)} usable images cached at {CACHE_DIR_FAMOUS}\n")

    print("Running CLIP/Qdrant search once per image...")
    raw_results = run_raw_searches(eval_set_famous, db)

    print("\n--- Threshold comparison ---")
    table = sweep_thresholds(raw_results, THRESHOLDS)
    print_threshold_table(table)

    output_path = "benchmarks/models/benchmark_threshold_famous.json"
    with open(output_path, "w") as f:
        json.dump({"raw": raw_results, "thresholds": table}, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {output_path}")
