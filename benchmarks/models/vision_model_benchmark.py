import base64
import json
import logging
import os
import random
import string
import time
from typing import Dict, List

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

from benchmarks.models.generate_dataset import load_eval_set
from src.agent.prompts import Prompts
from src.agent.tools.llm_tools import ChatArtworkInfo, _describe_api_error, _is_transient

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING)

CACHE_DIR = "benchmarks/models/bench_cache/famous"
LANGUAGE = "en"
N_WORDS = 100
SECONDS_BETWEEN_MODELS = 1  # small buffer so rate limits don't pile up across models

SUBSET_SIZE = 20

LANGUAGE_MAPPER = {"ca": "català", "es": "español", "en": "english"}
MODEL_ATTEMPTS = 2
MODEL_RETRY_WAIT = 2  # seconds, multiplied by the attempt number

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


def build_vision_llm(candidate: Dict):
    """Returns (vision_llm, structured_output_method) for one candidate model.

    Deliberately does NOT construct an LLMTools instance: LLMTools.identify_artwork
    now runs a two-model blind+judge ensemble (3+ calls per image), which measures
    the ensemble's behavior, not a single model's own identification quality. This
    benchmark wants the latter, so it talks to the model directly instead.
    """
    provider = candidate["provider"]
    if provider == "groq":
        vision_llm = init_chat_model(
            model=candidate["model"],
            model_provider="openai",
            api_key=os.environ["GROQ_API_KEY"],
            base_url="https://api.groq.com/openai/v1",
            reasoning_effort="none",
        )
        return vision_llm, "json_mode"
    elif provider == "mistralai":
        vision_llm = init_chat_model(
            model=candidate["model"],
            model_provider="mistralai",
            api_key=os.environ["MISTRAL_API_KEY"],
        )
        return vision_llm, "json_schema"
    else:
        raise ValueError(f"Unknown provider: {provider!r}")


def identify_artwork_raw(vision_llm, structured_output_method: str, image_path: str) -> Dict:
    """Single raw identification call, same prompt/schema production uses, no
    ensemble machinery -- this is what LLMTools.identify_artwork used to be
    before it grew into the blind+judge pipeline. Reuses Prompts/ChatArtworkInfo
    straight from production so the benchmark stays in sync if the prompt changes.
    """
    llm_artwork_info = vision_llm.with_structured_output(
        ChatArtworkInfo, method=structured_output_method
    )

    with open(image_path, "rb") as img:
        image_b64 = base64.b64encode(img.read()).decode("utf-8")
    image_content = {
        "type": "image_url",
        "image_url": {"url": "data:image/jpeg;base64," + image_b64},
    }

    prompt = Prompts.ART_IDENTIFICATION_PROMPT.format(
        language=LANGUAGE_MAPPER[LANGUAGE], n_words=N_WORDS, candidate_hint=""
    )
    messages = [
        SystemMessage(content=Prompts.SYSTEM_GUIDELINES),
        HumanMessage(content=[{"type": "text", "text": prompt}, image_content]),
    ]

    for attempt in range(1, MODEL_ATTEMPTS + 1):
        try:
            response = llm_artwork_info.invoke(messages)
            return response.to_dict()
        except Exception as exc:
            logging.error(
                f"Vision identification failed (attempt {attempt}/{MODEL_ATTEMPTS}): "
                f"{_describe_api_error(exc)}"
            )
            if attempt == MODEL_ATTEMPTS or not _is_transient(exc):
                raise
            time.sleep(MODEL_RETRY_WAIT * attempt)


def evaluate_model(candidate: Dict, eval_set: List[Dict]) -> Dict:
    label = f"{candidate['provider']}/{candidate['model']}"
    vision_llm, structured_output_method = build_vision_llm(candidate)

    hard_errors = (
        0  # provider/parsing exception, not recovered by identify_artwork_raw's own retries
    )
    empty_titles = 0  # no exception, but the model gave up on identifying anything
    wrong_titles = 0  # identified *something*, but not the actual artwork
    correct = 0
    details = []  # per-image comparison, persisted below (not just the aggregate counts)

    for i, item in enumerate(eval_set, 1):
        try:
            painting = identify_artwork_raw(
                vision_llm, structured_output_method, item["image_path"]
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
