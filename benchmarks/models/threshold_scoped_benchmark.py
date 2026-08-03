import base64
import io
import json
import logging
from typing import Dict, List

from dotenv import load_dotenv
from PIL import Image
from qdrant_client.models import Filter, HasIdCondition

from benchmarks.models.generate_dataset import load_eval_set
from benchmarks.models.utils import print_threshold_table, sweep_thresholds, THRESHOLDS
from src.services.qdrant_db import QdrantDB

logging.getLogger("src.services.qdrant_db").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)
logging.getLogger("qdrant_client").setLevel(logging.ERROR)
logging.getLogger("src.services.qdrant_db").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

logging.basicConfig(level=logging.ERROR)

CACHE_DIR_FAMOUS = "benchmarks/models/bench_cache/famous"
CACHE_DIR_RANDOM = "benchmarks/models/bench_cache/random"


def search_within_catalog(
    db: QdrantDB, image_b64: str, catalog_ids: List[str], top_k: int = 5
) -> List[Dict]:

    image_bytes = base64.b64decode(image_b64)
    img = Image.open(io.BytesIO(image_bytes))
    try:
        img_embedding = db.model.encode(img)
    finally:
        img.close()

    results = db.client.search(
        collection_name=db.collection_name,
        query_vector=img_embedding.tolist(),
        query_filter=Filter(must=[HasIdCondition(has_id=catalog_ids)]),
        limit=top_k,
    )
    return [
        {"title": hit.payload["title"], "artist": hit.payload["artist"], "score": hit.score}
        for hit in results
    ]


def run_raw_searches_scoped(
    eval_set: List[Dict], catalog_ids: List[str], db: QdrantDB
) -> List[Dict]:
    raw = []
    for i, item in enumerate(eval_set, 1):
        with open(item["image_path"], "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("utf-8")

        try:
            results = search_within_catalog(db, image_b64, catalog_ids)
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
    catalog_ids = [item["id"] for item in eval_set_random]
    print(
        f"Loaded {len(eval_set_random)} items from {CACHE_DIR_RANDOM} as both the query images "
        f"and the simulated catalog ({len(catalog_ids)} candidates, instead of the "
        f"whole production collection)\n"
    )

    print("Running scoped CLIP/Qdrant search (catalog-restricted) once per image...")
    raw_results = run_raw_searches_scoped(eval_set_random, catalog_ids, db)

    print("\n--- Threshold comparison (scoped catalog) ---")
    table = sweep_thresholds(raw_results, THRESHOLDS)
    print_threshold_table(table)

    output_path = "benchmarks/models/benchmark_threshold_scoped_random.json"
    with open(output_path, "w") as f:
        json.dump({"raw": raw_results, "thresholds": table}, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {output_path}")

    eval_set_famous = load_eval_set(CACHE_DIR_FAMOUS)
    catalog_ids = [item["id"] for item in eval_set_famous]
    print(
        f"Loaded {len(eval_set_famous)} items from {CACHE_DIR_FAMOUS} as both the query images "
        f"and the simulated catalog ({len(catalog_ids)} candidates, instead of the "
        f"whole production collection)\n"
    )

    print("Running scoped CLIP/Qdrant search (catalog-restricted) once per image...")
    raw_results = run_raw_searches_scoped(eval_set_famous, catalog_ids, db)

    print("\n--- Threshold comparison (scoped catalog) ---")
    table = sweep_thresholds(raw_results, THRESHOLDS)
    print_threshold_table(table)

    output_path = "benchmarks/models/benchmark_threshold_scoped_famous.json"
    with open(output_path, "w") as f:
        json.dump({"raw": raw_results, "thresholds": table}, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {output_path}")
