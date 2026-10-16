#!/usr/bin/env python3
"""
extract_features.py — run the verifier once over the perturbation set and
store the RAW mechanism outputs.

WHY RAW FEATURES AND NOT THE FINAL SCORE
    NLI is the expensive part of the pipeline. Storing only the combined
    score would mean re-running it every time you wanted to test a different
    way of combining the mechanisms. Storing the raw per-mechanism outputs
    means every combination rule — including ones not thought of yet — can be
    evaluated offline in seconds.

    This is also what makes the "0.30 / 0.70 weighting is arbitrary" objection
    answerable: you can compare five combination rules on identical inputs
    rather than defending one.

WHAT IT REPLICATES
    For a single evidence chunk, verify_claim() does:

        sim = _semantic_similarity(claim, chunk)
        if sim < SIMILARITY_GATE:  -> UNSUPPORTED, score 0
        nli = _nli_scores(claim, chunk)
        if contradiction_p > CONTRADICTION_THRESH:  combined = 0
        else: combined = 0.30*sim + 0.70*entailment_p
        combined *= entity.score   (if it fired)
        combined *= negation.score (if it fired)
        verdict from contradiction_p and combined

    Every row of the perturbation set has exactly one evidence chunk, so the
    logic above is reproduced here with each intermediate recorded.

USAGE
    python -m src.extract_features
    python -m src.extract_features --limit 20     # quick trial
"""
from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

from src.trust_layer.verifier import (
    CONTRADICTION_THRESH,
    SIMILARITY_GATE,
    SUPPORTED_SCORE,
    _NLI_CONTRADICTION,
    _NLI_ENTAILMENT,
    _NLI_NEUTRAL,
    _entity_match,
    _negation_check,
    _nli_scores,
    _semantic_similarity,
)

OUT_FIELDS = [
    "pair_id", "source", "perturbation_type", "label", "split",
    "similarity", "gate_passed",
    "entailment_p", "contradiction_p", "neutral_p",
    "entity_fired", "entity_score",
    "negation_fired", "negation_score",
    "combined_score", "verdict",
    "claim", "evidence_source",
]


def features_for(claim: str, evidence: str, granularity: str = "chunk") -> dict:
    """Run every mechanism on one (claim, evidence) pair and record it all."""
    sim = _semantic_similarity(claim, evidence)

    if sim < SIMILARITY_GATE:
        # verify_claim skips the chunk entirely; with only one chunk that
        # means no candidate survived and the verdict is UNSUPPORTED at 0.0.
        return dict(
            similarity=sim, gate_passed=0,
            entailment_p="", contradiction_p="", neutral_p="",
            entity_fired="", entity_score="",
            negation_fired="", negation_score="",
            combined_score=0.0, verdict="UNSUPPORTED",
        )

    probs = _nli_scores(claim, evidence, granularity=granularity)
    contradiction_p = float(probs[_NLI_CONTRADICTION])
    entailment_p = float(probs[_NLI_ENTAILMENT])
    neutral_p = float(probs[_NLI_NEUTRAL])

    if contradiction_p > CONTRADICTION_THRESH:
        combined = 0.0
    else:
        combined = 0.30 * sim + 0.70 * entailment_p

    entity = _entity_match(claim, evidence)
    negation = _negation_check(claim, evidence)
    if entity.fired:
        combined *= entity.score
    if negation.fired:
        combined *= negation.score

    if contradiction_p > CONTRADICTION_THRESH:
        verdict = "CONTRADICTION"
    elif combined >= SUPPORTED_SCORE:
        verdict = "SUPPORTED"
    else:
        verdict = "UNSUPPORTED"

    return dict(
        similarity=sim, gate_passed=1,
        entailment_p=entailment_p,
        contradiction_p=contradiction_p,
        neutral_p=neutral_p,
        entity_fired=int(entity.fired), entity_score=entity.score,
        negation_fired=int(negation.fired), negation_score=negation.score,
        combined_score=combined, verdict=verdict,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pert", type=Path,
                    default=Path("data/processed/perturbations.csv"))
    ap.add_argument("--out", type=Path,
                    default=Path("data/processed/features.csv"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--nli-model", default=None,
                    help="override the NLI checkpoint, e.g. "
                         "cross-encoder/nli-deberta-v3-large")
    ap.add_argument("--nli-granularity", choices=("chunk", "sentence"),
                    default="chunk",
                    help="premise handed to the NLI model: the whole chunk "
                         "(default) or each sentence, aggregated by per-label max")
    args = ap.parse_args()

    with args.pert.open(encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    if args.limit:
        rows = rows[: args.limit]
    print(f"Loaded {len(rows)} rows from {args.pert}")
    if args.nli_model:
        from src.trust_layer.verifier import set_nli_model
        set_nli_model(args.nli_model)
    from src.trust_layer.verifier import NLI_MODEL_NAME
    print(f"NLI model      : {NLI_MODEL_NAME}")
    print(f"NLI granularity: {args.nli_granularity}")

    out = []
    started = time.time()
    for i, r in enumerate(rows, 1):
        claim = (r.get("claim") or "").strip()
        evidence = (r.get("evidence") or "").strip()
        if not claim or not evidence:
            continue
        f = features_for(claim, evidence, args.nli_granularity)
        f.update(
            pair_id=r["pair_id"], source=r.get("source", ""),
            perturbation_type=r["perturbation_type"],
            label=r["label"], split=r["split"],
            claim=claim, evidence_source=r.get("evidence_source", ""),
        )
        out.append(f)
        if i % 25 == 0 or i == len(rows):
            rate = i / max(time.time() - started, 1e-9)
            print(f"  {i}/{len(rows)}  ({rate:.1f} rows/s)")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=OUT_FIELDS)
        w.writeheader()
        w.writerows(out)

    from collections import Counter
    print(f"\nWrote {len(out)} rows to {args.out}")
    print(" verdicts:", dict(Counter(r["verdict"] for r in out)))
    gated = sum(1 for r in out if not r["gate_passed"])
    print(f" rows that failed the similarity gate ({SIMILARITY_GATE}): {gated}")
    print("\nNext:  python -m src.evaluate_verifier")


if __name__ == "__main__":
    main()
