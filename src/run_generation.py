#!/usr/bin/env python3
"""
run_generation.py — THE FREEZE.

Runs retrieval and generation over the benchmark and writes one JSON record
per question. Nothing downstream ever regenerates: every later experiment —
different scoring rules, thresholds, aggregators, even a different verifier —
reads this file.

WHY FREEZE
    Generation is the only slow step (~10s per question through Ollama) and
    it is also the step that must stay CONSTANT across configurations. If
    Config B and Config D score different generated answers, the comparison
    is meaningless. EVALUATION_PLAN.md Layer 1.

    The saved record is also Config A for free: an unverified RAG baseline is
    exactly this file with no trust layer applied.

USAGE
    python -m src.run_generation
    python -m src.run_generation --limit 5      # smoke test
"""
from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

from src.rag.generator import MODEL_NAME, generate_answer
from src.rag.retriever import load_vectorstore, retrieve


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--qa", type=Path,
                    default=Path("data/processed/qa_pairs_labeled.csv"))
    ap.add_argument("--out", type=Path,
                    default=Path("data/processed/generations.jsonl"))
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--chroma", default=None,
                    help="index directory; defaults to data/chroma")
    ap.add_argument("--prompt", choices=("minimal", "grounded", "guarded"),
                    default="guarded",
                    help="how much the prompt constrains the model; see "
                         "generator.py for why this is a measured condition")
    ap.add_argument("--resume", action="store_true",
                    help="skip questions already present in --out")
    args = ap.parse_args()

    rows = list(csv.DictReader(args.qa.open(encoding="utf-8-sig")))
    if args.limit:
        rows = rows[: args.limit]

    done = set()
    if args.resume and args.out.exists():
        for line in args.out.open(encoding="utf-8"):
            done.add(json.loads(line)["question_id"])
        print(f"Resuming — {len(done)} already generated")

    print(f"{len(rows)} questions | model {MODEL_NAME} | k={args.k} | prompt={args.prompt}")
    print(f"index          : {args.chroma or 'data/chroma (default)'}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    vectorstore = load_vectorstore(args.chroma) if args.chroma else load_vectorstore()

    mode = "a" if (args.resume and args.out.exists()) else "w"
    started = time.time()
    with args.out.open(mode, encoding="utf-8") as fh:
        for i, row in enumerate(rows):
            if i in done:
                continue
            question = (row.get("question") or "").strip()
            if not question:
                continue

            t0 = time.time()
            chunks = retrieve(question, vectorstore, k=args.k)
            t1 = time.time()
            try:
                answer = generate_answer(question, chunks,
                                         prompt_mode=args.prompt)
                error = None
            except Exception as exc:              # Ollama down, timeout, ...
                answer, error = "", f"{type(exc).__name__}: {exc}"
            t2 = time.time()

            fh.write(json.dumps({
                "question_id": i,
                "question": question,
                "gold_answer": (row.get("gold_answer") or "").strip(),
                "expected_decision": (row.get("expected_decision") or "").strip(),
                "generated_answer": answer,
                "error": error,
                "retrieval_ms": round((t1 - t0) * 1000, 1),
                "generation_ms": round((t2 - t1) * 1000, 1),
                "retrieved_chunks": [
                    {"content": c.page_content,
                     "source_file": c.metadata.get("source_file", "unknown"),
                     "page": c.metadata.get("page", "?")}
                    for c in chunks
                ],
            }, ensure_ascii=False) + "\n")
            fh.flush()                            # survive an interrupt

            elapsed = time.time() - started
            n = i + 1 - len(done)
            print(f"  {i+1}/{len(rows)}  {elapsed/max(n,1):.1f}s/question"
                  + (f"  ERROR: {error}" if error else ""))

    print(f"\nWrote {args.out}")
    print("Next:  python -m src.run_verification")


if __name__ == "__main__":
    main()
