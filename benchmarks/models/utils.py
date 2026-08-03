from typing import Dict, List

THRESHOLDS = [0.15, 0.18, 0.20, 0.22, 0.25, 0.28, 0.30, 0.32, 0.35, 0.40]


def is_match(returned_title: str, expected_title: str) -> bool:
    """Loose ground-truth match: case/whitespace-insensitive exact title comparison."""
    if not returned_title or not expected_title:
        return False
    return returned_title.strip().casefold() == expected_title.strip().casefold()


def print_threshold_table(table: List[Dict]) -> None:
    print(f"{'threshold':>9} | {'accepted':>8} | {'precision':>9} | {'recall':>7} | tp/fp/fn/tn")
    for row in table:
        print(
            f"{row['threshold']:>9} | {row['accepted']:>8} | "
            f"{row['precision']!s:>9} | {row['recall']!s:>7} | "
            f"{row['tp']}/{row['fp']}/{row['fn']}/{row['tn']}"
        )


def sweep_thresholds(raw: List[Dict], thresholds: List[float]) -> List[Dict]:
    """For each candidate threshold, classify every cached result as:
    - TP: accepted (score >= threshold) and top-1 title is actually correct
    - FP: accepted but top-1 title is wrong -- the risky case, a wrong description
          gets played to the visitor with false confidence
    - FN: rejected but top-1 title was actually correct -- unnecessary, costlier
          detour through the deep-search fallback
    - TN: rejected and top-1 title was wrong -- correctly deferred to deep search
    """
    rows = []
    for threshold in thresholds:
        tp = fp = fn = tn = 0
        for r in raw:
            correct = is_match(r["top1_title"], r["expected"])
            accepted = r["score"] >= threshold
            if accepted and correct:
                tp += 1
            elif accepted and not correct:
                fp += 1
            elif not accepted and correct:
                fn += 1
            else:
                tn += 1

        accepted_n = tp + fp
        precision = round(tp / accepted_n, 3) if accepted_n else None  # trust in acceptances
        recall = round(tp / (tp + fn), 3) if (tp + fn) else None  # coverage of true matches
        rows.append(
            {
                "threshold": threshold,
                "accepted": accepted_n,
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "tn": tn,
                "precision": precision,
                "recall": recall,
            }
        )
    return rows
