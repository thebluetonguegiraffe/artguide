import json
import logging
import os
import random
import string
import time
from typing import Dict, List

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from benchmarks.models.generate_dataset import load_eval_set
from src.agent.tools.llm_tools import LLMTools

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING)

CACHE_DIR = "benchmarks/models/bench_cache/famous"
LANGUAGE = "en"
N_WORDS = 100
SECONDS_BETWEEN_MODELS = 1  # small buffer so rate limits don't pile up across models

SUBSET_SIZE = 20

VISION_MODELS = [
    {"model": "ministral-8b-2512", "provider": "mistralai"},
    {"model": "mistral-small-2603", "provider": "mistralai"},
    {"model": "qwen/qwen3.6-27b", "provider": "groq"},
]


_LEADING_ARTICLES = ("the ", "a ", "an ")


def subset(eval_set: List[Dict], n: int, seed: int = 42) -> List[Dict]:
    if n >= len(eval_set):
        return eval_set
    return random.Random(seed).sample(eval_set, n)


def _normalize_title(title: str) -> str:
    t = title.strip().strip(string.punctuation + " ").casefold()
    for article in _LEADING_ARTICLES:
        if t.startswith(article):
            t = t[len(article) :]  # noqa:E203
            break
    return t.strip()


def _plural_variant(a: str, b: str) -> bool:
    """True if one string becomes the other by adding a common plural suffix
    (e.g. "iris" / "irises", "flower" / "flowers")."""
    for suffix in ("s", "es"):
        if a + suffix == b or b + suffix == a:
            return True
    return False


def is_match(returned_title: str, expected_title: str) -> bool:
    if not returned_title or not expected_title:
        return False

    a = _normalize_title(returned_title)
    b = _normalize_title(expected_title)

    return a == b or _plural_variant(a, b)


def build_llm_tools(candidate: Dict) -> LLMTools:
    provider = candidate["provider"]
    if provider == "groq":
        structured_output_method = "json_mode"
        vision_llm = init_chat_model(
            model=candidate["model"],
            model_provider="openai",
            api_key=os.environ["GROQ_API_KEY"],
            base_url="https://api.groq.com/openai/v1",
            reasoning_effort="none",
        )
    elif provider == "mistralai":
        structured_output_method = "json_schema"
        vision_llm = init_chat_model(
            model=candidate["model"],
            model_provider="mistralai",
            api_key=os.environ["MISTRAL_API_KEY"],
        )
    else:
        raise ValueError(f"Unknown provider: {provider!r}")

    return LLMTools(
        llm=vision_llm, vision_llm=vision_llm, structured_output_method=structured_output_method
    )


def evaluate_model(candidate: Dict, eval_set: List[Dict]) -> Dict:
    label = f"{candidate['provider']}/{candidate['model']}"
    llm_tools = build_llm_tools(candidate)

    hard_errors = 0  # provider/parsing exception, not recovered by LLMTools' own retries
    empty_titles = 0  # no exception, but the model gave up on identifying anything
    wrong_titles = 0  # identified *something*, but not the actual artwork
    correct = 0
    details = []  # per-image comparison, persisted below (not just the aggregate counts)

    for i, item in enumerate(eval_set, 1):
        try:
            painting = llm_tools.identify_artwork(
                image_path=item["image_path"], language=LANGUAGE, n_words=N_WORDS
            )
        except Exception as exc:
            hard_errors += 1
            print(f"  [{label}] [{i}/{len(eval_set)}] ERROR: {exc}")
            details.append(
                {
                    "index": i,
                    "expected_title": item["title"],
                    "returned_title": None,
                    "returned_artist": None,
                    "outcome": "error",
                    "error": str(exc),
                }
            )
            continue

        if not painting.get("title"):
            empty_titles += 1
            print(f"  [{label}] [{i}/{len(eval_set)}] empty title " f"(expected {item['title']!r})")
            details.append(
                {
                    "index": i,
                    "expected_title": item["title"],
                    "returned_title": None,
                    "returned_artist": painting.get("artist"),
                    "outcome": "empty",
                    "error": None,
                }
            )
            continue

        matched = is_match(painting["title"], item["title"])
        if matched:
            correct += 1
        else:
            wrong_titles += 1
            print(
                f"  [{label}] [{i}/{len(eval_set)}] mismatch: "
                f"got {painting['title']!r}, expected {item['title']!r}"
            )
        details.append(
            {
                "index": i,
                "expected_title": item["title"],
                "returned_title": painting["title"],
                "returned_artist": painting.get("artist"),
                "outcome": "correct" if matched else "wrong",
                "error": None,
            }
        )

    total = len(eval_set)
    n_errors = hard_errors + empty_titles + wrong_titles
    return {
        "model": label,
        "total": total,
        "hard_errors": hard_errors,
        "empty_titles": empty_titles,
        "wrong_titles": wrong_titles,
        "correct": correct,
        "error_rate_pct": round(100 * n_errors / total, 1) if total else None,
        "details": details,
    }


def print_title_comparison(label: str, details: List[Dict]) -> None:
    """All expected-vs-returned title pairs for one model, hits included -- the
    per-row print during evaluate_model only shows failures, this is the full set
    for manually eyeballing matches too (e.g. to catch cases like a translated
    proper name that is_match won't flag but isn't really wrong either).
    """
    print(f"\n  Title comparison -- {label}")
    print(f"  {'#':>3} {'outcome':<8} {'expected':<38} {'returned':<38}")
    for d in details:
        expected = d["expected_title"] or ""
        returned = d["returned_title"] or ("<error>" if d["outcome"] == "error" else "<empty>")
        print(f"  {d['index']:>3} {d['outcome']:<8} {expected:<38} {returned:<38}")


if __name__ == "__main__":
    load_dotenv()

    eval_set = subset(load_eval_set(CACHE_DIR), SUBSET_SIZE)
    print(f"  using {len(eval_set)} of the cached images (subset cap={SUBSET_SIZE})")

    total_calls = len(eval_set) * len(VISION_MODELS)
    print(f"  {len(VISION_MODELS)} models x {len(eval_set)} images = {total_calls} vision calls\n")

    results = []
    for candidate in VISION_MODELS:
        label = f"{candidate['provider']}/{candidate['model']}"
        print(f"\n[MODEL] {label}")
        result = evaluate_model(candidate, eval_set)
        results.append(result)
        print_title_comparison(label, result["details"])
        time.sleep(SECONDS_BETWEEN_MODELS)

    print("\n--- Vision model comparison (always routed to deep search) ---")
    print(f"{'model':<48} | {'error %':>7} | hard/empty/wrong/correct")
    for r in results:
        print(
            f"{r['model']:<48} | {r['error_rate_pct']!s:>7} | "
            f"{r['hard_errors']}/{r['empty_titles']}/{r['wrong_titles']}/{r['correct']}"
        )

    output_path = "benchmarks/models/benchmark_vision_fallback_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {output_path}")
