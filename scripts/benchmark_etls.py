import time
import json
import logging
from dotenv import load_dotenv
from src.etl.implementations.wikiart_etl import WikiArtETL

logging.getLogger("src").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING)

SAMPLE_SIZE = 100
BATCH_SIZE = 10
WORKER_CONFIGS = [1, 2, 4, 8]


class BenchmarkWikiArtETL(WikiArtETL):
    """WikiArtETL with a dummy load() and a sample cap on extract()."""

    def __init__(self, workers: int, sample_size: int, batch_size: int):
        super().__init__(batch_size=batch_size, workers=workers)
        self.sample_size = sample_size
        self._extracted = 0

    def extract(self):
        for batch in super().extract():
            remaining = self.sample_size - self._extracted
            if remaining <= 0:
                break
            capped = batch[:remaining]
            self._extracted += len(capped)
            yield capped
            if self._extracted >= self.sample_size:
                break

    def load(self, batch):
        """Dummy load — no writes to Qdrant."""
        time.sleep(0.01)  # simulate minimal I/O


def run_sequential(workers: int, sample_size: int, batch_size: int) -> dict:
    """No pipeline threading — simple loop: extract > transform > load."""
    etl = BenchmarkWikiArtETL(workers=workers, sample_size=sample_size, batch_size=batch_size)
    total_processed = 0

    start = time.perf_counter()
    for batch in etl.extract():
        enriched = etl.transform(batch)
        etl.load(enriched)
        total_processed += len(batch)
    elapsed = round(time.perf_counter() - start, 3)
    throughput = round(total_processed / elapsed, 2)

    label = f"sequential (workers={workers})"
    print(f"  {label}: {elapsed}s — {throughput} artworks/s")
    return {
        "mode": "sequential",
        "workers": workers,
        "total_paintings": total_processed,
        "elapsed_seconds": elapsed,
        "throughput_per_second": throughput,
    }


def run_threaded(workers: int, sample_size: int, batch_size: int) -> dict:
    """Full pipeline threading: Extract / Transform / Load in separate threads."""
    etl = BenchmarkWikiArtETL(workers=workers, sample_size=sample_size, batch_size=batch_size)

    start = time.perf_counter()
    etl.run()  # uses BasePaintingsETL.run() with threading
    elapsed = round(time.perf_counter() - start, 3)

    throughput = round(sample_size / elapsed, 2)
    label = f"threaded (workers={workers})"
    print(f"  {label}: {elapsed}s — {throughput} artworks/s")
    return {
        "mode": "threaded",
        "workers": workers,
        "total_paintings": sample_size,
        "elapsed_seconds": elapsed,
        "throughput_per_second": throughput,
    }


if __name__ == "__main__":
    load_dotenv()

    results = []

    print("\n[SEQUENTIAL — no pipeline threads, 1 transform worker]")
    results.append(run_sequential(workers=1, sample_size=SAMPLE_SIZE, batch_size=BATCH_SIZE))

    print("\n[THREADED — pipeline threads enabled, varying transform workers]")
    for n_workers in WORKER_CONFIGS:
        print(f"\n  Config: workers={n_workers}")
        results.append(
            run_threaded(workers=n_workers, sample_size=SAMPLE_SIZE, batch_size=BATCH_SIZE)
        )

    print("\n--- Results ---")
    for r in results:
        label = f"{r['mode']} workers={r['workers']}"
        print(f"  {label}: {r['throughput_per_second']} artworks/s ({r['elapsed_seconds']}s)")

    output_path = "scripts/benchmark_etl_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_path}")
