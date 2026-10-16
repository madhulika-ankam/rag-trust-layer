#!/usr/bin/env python3
"""
run_verification.py — run the trust layer over the frozen generations.

Reads generations.jsonl, decomposes each answer into claims, verifies each
claim against that answer's retrieved chunks, and writes one record per
question with the RAW per-claim mechanism outputs.

Nothing here regenerates an answer. Re-running with a different NLI
granularity or model re-verifies the SAME frozen text, which is what makes
configurations comparable at all.

Per-claim features are stored rather than a final score so that scoring
rules, aggregators and thresholds can be compared offline without re-running
the verifier — the same reason extract_features.py stores them.

USAGE
    python -m src.run_verification
    python -m src.run_verification --nli-granularity sentence   (default)
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import src.trust_layer.verifier as V
from src.trust_layer.decomposer import decompose


class _Chunk:
    """Minimal stand-in for a LangChain Document, from the frozen JSON."""
    def __init__(self, d):
        self.page_content = d["content"]
        self.metadata = {"source_file": d["source_file"], "page": d["page"]}


# Phrases a model uses when it declines rather than asserts. A decline is not
# a factual claim and must not be verified as one — doing so turns an honest
# "I don't know" into a CONTRADICTION and then a false ESCALATE. This is the
# Q80 bug recorded in CONTEXT.md section C2.
_DECLINE_MARKERS = (
    "does not contain", "not contain enough", "no information",
    "does not provide", "not provided in the context",
    "cannot answer", "unable to answer", "not specified in the context",
    "the context does not", "insufficient information",
)


def looks_like_a_decline(answer: str) -> bool:
    a = answer.lower()
    return any(m in a for m in _DECLINE_MARKERS)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", type=Path,
                    default=Path("data/processed/generations.jsonl"))
    ap.add_argument("--out", type=Path,
                    default=Path("data/processed/verified.jsonl"))
    ap.add_argument("--nli-granularity", choices=("chunk", "sentence"),
                    default="sentence")
    ap.add_argument("--nli-model", default=None)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    if args.nli_model:
        V.set_nli_model(args.nli_model)
    V.NLI_GRANULARITY = args.nli_granularity

    records = [json.loads(l) for l in args.gen.open(encoding="utf-8")]
    if args.limit:
        records = records[: args.limit]
    print(f"{len(records)} frozen generations | NLI {V.NLI_MODEL_NAME} "
          f"| granularity {args.nli_granularity}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    started = time.time()
    with args.out.open("w", encoding="utf-8") as fh:
        for n, rec in enumerate(records, 1):
            answer = rec["generated_answer"]
            chunks = [_Chunk(c) for c in rec["retrieved_chunks"]]

            declined = looks_like_a_decline(answer)
            claims = [] if (declined or not answer.strip()) else decompose(answer)
            results = V.verify(claims, chunks) if claims else []

            fh.write(json.dumps({
                "question_id": rec["question_id"],
                "question": rec["question"],
                "gold_answer": rec["gold_answer"],
                "expected_decision": rec["expected_decision"],
                "generated_answer": answer,
                "declined_to_answer": declined,
                "generation_ms": rec["generation_ms"],
                "retrieval_ms": rec["retrieval_ms"],
                # float() throughout: numpy float32 is not JSON serialisable
                "claims": [{
                    "claim": r.claim,
                    "verdict": r.verdict,
                    "combined": float(r.score),
                    "source": r.best_chunk_source,
                    "contradiction_p": float((r.nli_probs or [0, 0, 0])[V._NLI_CONTRADICTION]),
                    "entailment_p": float((r.nli_probs or [0, 0, 0])[V._NLI_ENTAILMENT]),
                    "similarity": float(next((m.score for m in r.mechanisms
                                              if m.name == "semantic_similarity"), 0.0)),
                    "entity_score": float(next((m.score for m in r.mechanisms
                                                if m.name == "entity_match"), 1.0)),
                    "negation_score": float(next((m.score for m in r.mechanisms
                                                  if m.name == "negation"), 1.0)),
                } for r in results],
            }, ensure_ascii=False) + "\n")

            if n % 20 == 0 or n == len(records):
                print(f"  {n}/{len(records)}  ({n/(time.time()-started):.1f}/s)")

    from collections import Counter
    recs = [json.loads(l) for l in args.out.open(encoding="utf-8")]
    print(f"\nWrote {args.out}")
    print(" answers that declined to answer:",
          sum(1 for r in recs if r["declined_to_answer"]))
    print(" claims per answer:",
          dict(Counter(len(r["claims"]) for r in recs)))
    print("\nNext:  python -m src.evaluate_system")


if __name__ == "__main__":
    main()
