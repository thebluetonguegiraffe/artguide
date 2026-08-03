import json
import logging
import os
import random
from typing import Dict, List

from dotenv import load_dotenv
import requests

from src.services.qdrant_db import QdrantDB

logging.getLogger("src.services.qdrant_db").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING)

logger = logging.getLogger(__name__)

N_FAMOUS = 100
N_RANDOM = 100

FAMOUS_DIR = "benchmarks/models/models/bench_cache/famous"
RANDOM_DIR = "benchmarks/models/models/bench_cache/random"


# WikiArt's CDN rejects the default python-requests user agent with a 403,
# so a browser-like one is used for the image downloads below.
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ArtGuideBenchmark/1.0)"}

FAMOUS_PAINTINGS = [
    # Renaissance / Northern Renaissance
    "Mona Lisa",
    "The Last Supper",
    "The Birth of Venus",
    "Primavera",
    "The School of Athens",
    "The Creation of Adam",
    "The Last Judgment",
    "The Arnolfini Portrait",
    "The Garden of Earthly Delights",
    "Hunters in the Snow",
    "The Tower of Babel",
    "Netherlandish Proverbs",
    "The Triumph of Death",
    "Landscape with the Fall of Icarus",
    "Massacre of the Innocents",
    "The Ambassadors",
    "Judith Slaying Holofernes",
    "Bacchus and Ariadne",
    "Venus of Urbino",
    # Dutch Golden Age / Baroque
    "Girl with a Pearl Earring",
    "The Night Watch",
    "The Milkmaid",
    "View of Delft",
    "The Anatomy Lesson of Dr. Nicolaes Tulp",
    "Danaë",
    "Self-Portrait with Two Circles",
    "The Calling of Saint Matthew",
    "The Raft of the Medusa",
    "Las Meninas",
    "Las Hilanderas",
    "La Maja Desnuda",
    "La Maja Vestida",
    "Charles IV of Spain and His Family",
    # Romanticism / 19th century
    "Wanderer above the Sea of Fog",
    "Liberty Leading the People",
    "The Third of May 1808",
    "Saturn Devouring His Son",
    "The Sleep of Reason Produces Monsters",
    "The Fighting Temeraire",
    "Rain, Steam and Speed",
    "Ophelia",
    "The Lady of Shalott",
    "Washington Crossing the Delaware",
    "The Death of Marat",
    "Napoleon Crossing the Alps",
    "The Oath of the Horatii",
    "Portrait of Madame X",
    "The Gulf Stream",
    "American Progress",
    "The Peaceable Kingdom",
    # Impressionism / Post-Impressionism
    "Impression, Sunrise",
    "A Sunday Afternoon on the Island of La Grande Jatte",
    "The Card Players",
    "Bal du moulin de la Galette",
    "Le Déjeuner sur l'herbe",
    "Olympia",
    "The Luncheon of the Boating Party",
    "Water Lilies",
    "Woman with a Parasol",
    "Boulevard Montmartre",
    "The Absinthe Drinker",
    "At the Moulin Rouge",
    "A Bar at the Folies-Bergère",
    "The Balcony",
    "Music in the Tuileries",
    "The Railway",
    "The Starry Night",
    "Sunflowers",
    "Café Terrace at Night",
    "The Bedroom",
    "Wheatfield with Crows",
    "Irises",
    "Self-Portrait with Bandaged Ear",
    "The Potato Eaters",
    "Portrait of Dr. Gachet",
    # Symbolism / Expressionism
    "The Scream",
    "The Kiss",
    "The Weeping Woman",
    # Cubism / early Modernism
    "Les Demoiselles d'Avignon",
    "The Old Guitarist",
    "Girl before a Mirror",
    "Three Musicians",
    "Guernica",
    "Nude Descending a Staircase, No. 2",
    "Composition VII",
    "Composition VIII",
    "Composition VI",
    "Composition with Red, Blue and Yellow",
    "Yellow-Red-Blue",
    "On White II",
    "Black Square",
    "Broadway Boogie Woogie",
    # Fauvism / Matisse
    "Woman with a Hat",
    "The Dance",
    "The Joy of Life",
    "Harmony in Red",
    "Nude, Green Leaves and Bust",
    # Surrealism
    "The Persistence of Memory",
    "The Elephant Celebes",
    "The Treachery of Images",
    "The Empire of Light",
    "Golconda",
    "The Son of Man",
    "The Human Condition",
    "Time Transfixed",
    "The Great Masturbator",
    "Swans Reflecting Elephants",
    "Metamorphosis of Narcissus",
    "The Two Fridas",
    # American Modernism
    "American Gothic",
    "Nighthawks",
    "Christina's World",
    # Abstract Expressionism / Pop Art
    "Autumn Rhythm",
    "Convergence",
    "No. 5, 1948",
    "Campbell's Soup Cans",
    "Marilyn Diptych",
    "Whaam!",
    "Drowning Girl",
    # Japanese ukiyo-e
    "The Great Wave off Kanagawa",
    # Misc. widely-known portraits
    "Whistler's Mother",
    "Portrait of a Man in a Turban",
]


def _manifest_path(cache_dir: str) -> str:
    return os.path.join(cache_dir, "manifest.json")


def _load_manifest(cache_dir: str) -> List[Dict]:
    path = _manifest_path(cache_dir)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return []


def _save_manifest(cache_dir: str, manifest: List[Dict]) -> None:
    with open(_manifest_path(cache_dir), "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def build_eval_set(
    n_samples: int,
    cache_dir: str,
    pool_size: int = 500,
    seed: int = 42,
    exclude_ids: set = None,
) -> List[Dict]:

    os.makedirs(cache_dir, exist_ok=True)

    cached = _load_manifest(cache_dir)
    if len(cached) >= n_samples:
        return cached[:n_samples]

    db = QdrantDB()
    exclude_ids = exclude_ids or set()

    pool = []
    for batch in db.scroll(batch_size=100, limit=max(1, pool_size // 100)):
        for point in batch:
            if point["id"] in exclude_ids:
                continue
            payload = point["payload"]
            if payload.get("image_url") and payload.get("title"):
                pool.append({"id": point["id"], **payload})
        if len(pool) >= pool_size:
            break

    random.seed(seed)
    random.shuffle(pool)

    manifest = []
    for candidate in pool:
        if len(manifest) >= n_samples:
            break

        image_path = os.path.join(cache_dir, f"{candidate['id']}.jpg")
        if not os.path.exists(image_path):
            try:
                resp = requests.get(candidate["image_url"], headers=HEADERS, timeout=15)
                resp.raise_for_status()
                with open(image_path, "wb") as f:
                    f.write(resp.content)
            except Exception as exc:
                logger.warning(f"Skipping {candidate['title']!r}: image download failed ({exc})")
                continue

        manifest.append(
            {
                "id": candidate["id"],
                "title": candidate["title"],
                "artist": candidate.get("artist"),
                "image_url": candidate["image_url"],
                "image_path": image_path,
            }
        )

    _save_manifest(cache_dir, manifest)
    return manifest


def _build_title_index(db: QdrantDB) -> Dict[str, List[Dict]]:
    """One full pass over the collection, keyed by casefolded title.

    Qdrant's payload filters do exact-string matches on keyword fields, which is
    unforgiving for a hand-typed title list (case, punctuation). Scrolling once and
    indexing client-side means every title in FAMOUS_PAINTINGS gets looked up
    against the same in-memory pass, instead of re-scrolling per title.
    """
    index: Dict[str, List[Dict]] = {}
    for batch in db.scroll(batch_size=200):
        for point in batch:
            title = point["payload"].get("title")
            if not title:
                continue
            index.setdefault(title.casefold(), []).append({"id": point["id"], **point["payload"]})
    return index


def load_eval_set(cache_dir: str) -> List[Dict]:
    manifest = _load_manifest(cache_dir)
    if not manifest:
        raise FileNotFoundError(
            f"No cached eval set found at {_manifest_path(cache_dir)!r}. "
            "Run build_eval_set() or build_named_eval_set() once first to generate it."
        )
    return manifest


def build_named_eval_set(titles: List[str], cache_dir: str, n_samples: int = None) -> List[Dict]:
    os.makedirs(cache_dir, exist_ok=True)

    cached = _load_manifest(cache_dir)
    if cached:
        return cached

    db = QdrantDB()
    index = _build_title_index(db)

    manifest = []
    not_found = []
    for query in titles:
        if n_samples is not None and len(manifest) >= n_samples:
            break

        query_cf = query.strip().casefold()
        candidates = index.get(query_cf)
        if not candidates:
            candidates = [points[0] for key, points in index.items() if query_cf in key]

        if not candidates:
            not_found.append(query)
            continue

        painting = candidates[0]
        image_path = os.path.join(cache_dir, f"{painting['id']}.jpg")
        if not os.path.exists(image_path):
            try:
                resp = requests.get(painting["image_url"], headers=HEADERS, timeout=15)
                resp.raise_for_status()
                with open(image_path, "wb") as f:
                    f.write(resp.content)
            except Exception as exc:
                logger.warning(f"Skipping {query!r}: image download failed ({exc})")
                not_found.append(query)
                continue

        manifest.append(
            {
                "id": painting["id"],
                "requested_as": query,
                "title": painting["title"],
                "artist": painting.get("artist"),
                "image_url": painting["image_url"],
                "image_path": image_path,
            }
        )

    if n_samples is not None and len(manifest) < n_samples:
        print(
            f"  Only found {len(manifest)}/{n_samples} requested titles -- "
            f"add more candidates to the titles list to close the gap."
        )
    if not_found:
        print(f"  Not found in Qdrant, skipped: {not_found}")

    _save_manifest(cache_dir, manifest)
    return manifest


if __name__ == "__main__":
    load_dotenv()

    print(f"Building famous set ({N_FAMOUS} target, {len(FAMOUS_PAINTINGS)} candidates)...")
    famous_set = build_named_eval_set(FAMOUS_PAINTINGS, cache_dir=FAMOUS_DIR, n_samples=N_FAMOUS)
    print(f"  {len(famous_set)} famous paintings cached at {FAMOUS_DIR}")
    print(f"  Names saved in {FAMOUS_DIR}/manifest.json")

    print(f"\nBuilding random set ({len(famous_set)} target, excluding the famous ones above)...")
    famous_ids = {item["id"] for item in famous_set}
    random_set = build_eval_set(
        n_samples=len(famous_set), cache_dir=RANDOM_DIR, exclude_ids=famous_ids
    )
    print(f"  {len(random_set)} random paintings cached at {RANDOM_DIR}")
    print(f"  Names saved in {RANDOM_DIR}/manifest.json")

    total = len(famous_set) + len(random_set)
    print(
        f"\nDataset ready: {total} paintings total ({len(famous_set)} famous + {len(random_set)} random)."  # noqa
    )
    if len(famous_set) < N_FAMOUS:
        print(
            f"  Note: only {len(famous_set)}/{N_FAMOUS} famous titles matched -- add more "
            f"candidates to FAMOUS_PAINTINGS in scripts/bench_dataset.py to close the gap."
        )
