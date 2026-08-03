import base64
# import json
import logging
import os
import time
from typing import Dict, List, Optional

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from benchmarks.models.generate_dataset import load_eval_set
from config import api_config
from src.agent.artguide_agent import ArtGuide  # reuse its thresholds, don't duplicate them
from src.agent.tools.api_tools import APITools
from src.agent.tools.base_tools import BaseTools
from src.agent.tools.llm_tools import LLMTools

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING)

CACHE_DIR = "benchmarks/models/bench_cache/famous"
LANGUAGE = "en"
N_WORDS = 100
SUBSET_SIZE = 20

# Only images that actually reach the vision fallback pay this cost -- fast-path
# hits go straight through CLIP/Qdrant and don't need spacing out.
SECONDS_BETWEEN_FALLBACK_CALLS = 1

TARGET_INDICES = {2, 7, 11, 16}


def subset(eval_set: List[Dict], n: int, seed: int = 42) -> List[Dict]:
    import random

    if n >= len(eval_set):
        return eval_set
    return random.Random(seed).sample(eval_set, n)


def build_tools():
    """Mirrors ArtGuide.__init__ exactly: same models, same roles, same
    thresholds (pulled from the class itself, not copy-pasted, so this stays in
    sync automatically if SCORE_THRESHOLD/SUGGESTION_THRESHOLD get retuned)."""
    mistral_2603_llm = init_chat_model(
        model="mistral-small-2603",
        model_provider="mistralai",
        api_key=os.environ["MISTRAL_API_KEY"],
    )
    mistral_8b_2512_llm = init_chat_model(
        model="ministral-8b-2512",
        model_provider="mistralai",
        api_key=os.environ["MISTRAL_API_KEY"],
    )
    llm_tools = LLMTools(
        description_model=mistral_2603_llm,
        first_vision_model=mistral_8b_2512_llm,
        second_vision_model=mistral_2603_llm,
        judge_model=mistral_2603_llm,
        structured_output_method="json_schema",
    )
    api_tools = APITools(api_config["url"])
    utils = BaseTools()
    return llm_tools, api_tools, utils


def route(clip_top1: Optional[Dict], utils: BaseTools) -> str:
    """Same branching identify_artwork's callers do in the real graph
    (route_deep_research + the candidate zone check inside deep_search_node),
    just pulled out here so the benchmark can report on it directly."""
    if not clip_top1:
        return "fallback_no_hint"

    score = clip_top1.get("score", 0)
    if utils.score_meets_threshold(score, ArtGuide.SCORE_THRESHOLD):
        return "clip_fast_path"
    if ArtGuide.SUGGESTION_THRESHOLD <= score < ArtGuide.SCORE_THRESHOLD:
        return "fallback_with_hint"
    return "fallback_no_hint"


def evaluate_pipeline(
    llm_tools: LLMTools, api_tools: APITools, utils: BaseTools, eval_set: List[Dict]
) -> Dict:
    path_counts = {"clip_fast_path": 0, "fallback_with_hint": 0, "fallback_no_hint": 0}
    hard_errors = 0
    empty_titles = 0  # fallback path only -- the judge gave up entirely
    durations_by_path: Dict[str, List[float]] = {
        "clip_fast_path": [],
        "fallback_with_hint": [],
        "fallback_no_hint": [],
    }
    details = []

    for i, item in enumerate(eval_set, 1):
        start = time.monotonic()
        try:
            with open(item["image_path"], "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode("utf-8")

            results = api_tools.search_painting(image_base64)
            clip_top1 = results[0] if results else None
            path = route(clip_top1, utils)
            path_counts[path] += 1

            if path == "clip_fast_path":
                returned_title = clip_top1.get("title")
                returned_artist = clip_top1.get("artist")
            else:
                candidate = clip_top1 if path == "fallback_with_hint" else None
                painting = llm_tools.identify_artwork(
                    image_path=item["image_path"],
                    language=LANGUAGE,
                    n_words=N_WORDS,
                    candidate=candidate,
                )
                returned_title = painting.get("title")
                returned_artist = painting.get("artist")
                if not returned_title:
                    empty_titles += 1
                time.sleep(SECONDS_BETWEEN_FALLBACK_CALLS)

        except Exception as exc:
            elapsed = time.monotonic() - start
            hard_errors += 1
            print(f"  [{i}/{len(eval_set)}] ERROR ({elapsed:.1f}s): {exc}")
            details.append(
                {
                    "index": i,
                    "expected_title": item["title"],
                    "clip_score": None,
                    "path": "error",
                    "returned_title": None,
                    "returned_artist": None,
                    "seconds": round(elapsed, 1),
                    "error": str(exc),
                }
            )
            continue

        elapsed = time.monotonic() - start
        durations_by_path[path].append(elapsed)
        clip_score = round(clip_top1.get("score", 0), 3) if clip_top1 else None

        print(
            f"  [{i}/{len(eval_set)}] ({elapsed:.1f}s) path={path} "
            f"clip_score={clip_score} -> {returned_title!r} (expected {item['title']!r})"
        )
        details.append(
            {
                "index": i,
                "expected_title": item["title"],
                "clip_score": clip_score,
                "path": path,
                "returned_title": returned_title,
                "returned_artist": returned_artist,
                "seconds": round(elapsed, 1),
                "error": None,
            }
        )

    total = len(eval_set)

    def _avg(path: str) -> Optional[float]:
        vals = durations_by_path[path]
        return round(sum(vals) / len(vals), 1) if vals else None

    return {
        "total": total,
        "path_counts": path_counts,
        "fallback_rate_pct": (
            round(
                100 * (path_counts["fallback_with_hint"] + path_counts["fallback_no_hint"]) / total,
                1,
            )
            if total
            else None
        ),
        "hard_errors": hard_errors,
        "empty_titles": empty_titles,
        "avg_seconds_clip_fast_path": _avg("clip_fast_path"),
        "avg_seconds_fallback_with_hint": _avg("fallback_with_hint"),
        "avg_seconds_fallback_no_hint": _avg("fallback_no_hint"),
        "details": details,
    }


def print_title_comparison(details: List[Dict]) -> None:
    """Full expected-vs-returned table for manual review, with the CLIP score and
    routing path attached so you can see *why* each image went where it went,
    not just what came out at the end."""
    print("\n  Title comparison (manual review)")
    print(
        f"  {'#':>3} {'path':<19} {'score':>6} {'seconds':>7} " f"{'expected':<36} {'returned':<36}"
    )
    for d in details:
        expected = d["expected_title"] or ""
        returned = d["returned_title"] or ("<error>" if d["path"] == "error" else "<empty>")
        score = d["clip_score"] if d["clip_score"] is not None else "-"
        print(
            f"  {d['index']:>3} {d['path']:<19} {score!s:>6} {d['seconds']:>7} "
            f"{expected:<36} {returned:<36}"
        )


if __name__ == "__main__":
    load_dotenv()

    # eval_set = subset(load_eval_set(CACHE_DIR), SUBSET_SIZE)

    # print(f"  using {len(eval_set)} of the cached images (subset cap={SUBSET_SIZE})")
    # print(
    #     f"  thresholds from ArtGuide: SCORE_THRESHOLD={ArtGuide.SCORE_THRESHOLD} "
    #     f"SUGGESTION_THRESHOLD={ArtGuide.SUGGESTION_THRESHOLD}\n"
    # )

    llm_tools, api_tools, utils = build_tools()
    # result = evaluate_pipeline(llm_tools, api_tools, utils, eval_set)
    # print_title_comparison(result["details"])

    # print("\n--- Full pipeline stats (CLIP + fallback) ---")
    # print(f"total: {result['total']}")
    # print(f"path_counts: {result['path_counts']}")
    # print(f"fallback_rate_pct: {result['fallback_rate_pct']}")
    # print(f"hard_errors: {result['hard_errors']}")
    # print(f"empty_titles (fallback only): {result['empty_titles']}")
    # print(f"avg_seconds clip_fast_path: {result['avg_seconds_clip_fast_path']}")
    # print(f"avg_seconds fallback_with_hint: {result['avg_seconds_fallback_with_hint']}")
    # print(f"avg_seconds fallback_no_hint: {result['avg_seconds_fallback_no_hint']}")

    # output_path = "benchmarks/models/benchmark_full_pipeline_results.json"
    # with open(output_path, "w") as f:
    #     json.dump(result, f, indent=2, ensure_ascii=False)
    # print(f"\nResults saved to {output_path}")
    eval_set = subset(load_eval_set(CACHE_DIR), SUBSET_SIZE)
    targets = [(i, item) for i, item in enumerate(eval_set, 1) if i in TARGET_INDICES]

    print(
        f"  isolating {len(targets)} of {len(eval_set)} cached images: {sorted(TARGET_INDICES)}\n"
    )

    for i, item in targets:
        print(f"\n{'=' * 70}\n[{i}] expected: {item['title']!r}\n{'=' * 70}")

        with open(item["image_path"], "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode("utf-8")

        results = api_tools.search_painting(image_base64)
        print("  CLIP top-5:")
        for rank, r in enumerate(results[:5], 1):
            print(f"    {rank}. {r.get('title')!r} (score={r.get('score'):.3f})")

        clip_top1 = results[0] if results else None
        path = route(clip_top1, utils)
        print(f"  routed to: {path}")

        if path == "clip_fast_path":
            print("  (fast path -- never reaches identify_artwork, nothing more to inspect here)")
            continue

        candidate = clip_top1 if path == "fallback_with_hint" else None
        painting = llm_tools.identify_artwork(
            image_path=item["image_path"],
            language=LANGUAGE,
            n_words=N_WORDS,
            candidate=candidate,
        )
        print(
            f"  final (post-judge): title={painting.get('title')!r} artist={painting.get('artist')!r}"  # noqa
        )
