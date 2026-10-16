#!/usr/bin/env python3
"""
granularity_by_length.py — is sentence-level NLI better for LONG claims too,
or only for short ones?

WHY THIS EXISTS
    The granularity decision (src/experiments/granularity.py) was taken on
    claims that are now mostly short. That leaves an obvious question
    unanswered: sentence-level wins ON THE CLAIMS WE HAVE, but does it win
    BECAUSE they are short?

    This is the only clean way to ask. The 302 perturbation pairs carry
    ground-truth labels and span 7 to 57 words, and the same pairs have been
    scored at both granularities (features.csv = chunk,
    features_sentence.csv = sentence). So the comparison can be run WITHIN
    each length band, with everything else held fixed.

    Each row is one claim against one evidence passage, so there is no
    multi-chunk aggregation confounding the result.

USAGE
    venv/bin/python src/experiments/granularity_by_length.py
"""
from __future__ import annotations

import csv
import statistics as st

BANDS = [(0, 15), (15, 20), (20, 30), (30, 999)]
FILES = {"chunk": "data/processed/features.csv",
         "sentence": "data/processed/features_sentence.csv"}


def auc(scores: list[float], labels: list[int]) -> float:
    """Mann-Whitney U / rank-based ROC-AUC, ties handled by average rank."""
    pairs = sorted(zip(scores, labels))
    ranks, i = [0.0] * len(pairs), 0
    while i < len(pairs):
        j = i
        while j + 1 < len(pairs) and pairs[j + 1][0] == pairs[i][0]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[k] = avg
        i = j + 1
    pos = sum(1 for _, l in pairs if l == 1)
    neg = len(pairs) - pos
    if pos == 0 or neg == 0:
        return float("nan")
    rank_sum = sum(r for r, (_, l) in zip(ranks, pairs) if l == 1)
    return (rank_sum - pos * (pos + 1) / 2) / (pos * neg)


def load(path: str) -> list[dict]:
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    for r in rows:
        r["_w"] = len(r["claim"].split())
        r["_y"] = 1 if r["label"] == "supported" else 0
        r["_s"] = float(r["combined_score"] or 0.0)
        r["_e"] = float(r["entailment_p"] or 0.0)
    return rows


def main() -> None:
    data = {name: load(path) for name, path in FILES.items()}
    n = len(data["sentence"])
    print(f"  {n} perturbation pairs, labelled. Same pairs scored at both")
    print("  granularities. AUC computed WITHIN each claim-length band.\n")
    print(f"  {'claim words':<14}{'n':>5}{'pos/neg':>10}"
          f"{'AUC chunk':>12}{'AUC sentence':>14}{'difference':>13}")
    print("  " + "-" * 68)

    for lo, hi in BANDS:
        sel = {k: [r for r in v if lo <= r["_w"] < hi] for k, v in data.items()}
        m = len(sel["sentence"])
        if m < 15:
            continue
        pos = sum(r["_y"] for r in sel["sentence"])
        a_c = auc([r["_s"] for r in sel["chunk"]], [r["_y"] for r in sel["chunk"]])
        a_s = auc([r["_s"] for r in sel["sentence"]], [r["_y"] for r in sel["sentence"]])
        label = f"{lo}-{hi}" if hi < 999 else f"{lo}+"
        flag = "  sentence" if a_s > a_c else ("  chunk" if a_c > a_s else "  tie")
        print(f"  {label:<14}{m:>5}{f'{pos}/{m - pos}':>10}"
              f"{a_c:>12.3f}{a_s:>14.3f}{a_s - a_c:>+13.3f}{flag}")

    print()
    a_c = auc([r["_s"] for r in data["chunk"]], [r["_y"] for r in data["chunk"]])
    a_s = auc([r["_s"] for r in data["sentence"]], [r["_y"] for r in data["sentence"]])
    print(f"  {'ALL':<14}{n:>5}{'':>10}{a_c:>12.3f}{a_s:>14.3f}{a_s - a_c:>+13.3f}")

    # Does sentence granularity rescue the entailment collapse, or only
    # soften it? Mean entailment on the SUPPORTED rows is the cleanest read:
    # those are the ones that should score high at any length.
    print("\n  mean entailment on SUPPORTED pairs only — the length collapse")
    print(f"  {'claim words':<14}{'n':>5}{'chunk':>10}{'sentence':>11}{'gain':>9}")
    print("  " + "-" * 50)
    for lo, hi in BANDS:
        sel = {k: [r for r in v if lo <= r["_w"] < hi and r["_y"] == 1]
               for k, v in data.items()}
        m = len(sel["sentence"])
        if m < 10:
            continue
        mc = st.mean(r["_e"] for r in sel["chunk"])
        ms = st.mean(r["_e"] for r in sel["sentence"])
        label = f"{lo}-{hi}" if hi < 999 else f"{lo}+"
        print(f"  {label:<14}{m:>5}{mc:>10.3f}{ms:>11.3f}{ms - mc:>+9.3f}")


if __name__ == "__main__":
    main()
