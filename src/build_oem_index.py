#!/usr/bin/env python3
"""
build_oem_index.py — a second index containing ONLY the three OEM manuals.

WHY
    Two manipulations, each of which alone changed little, applied together:

      minimal prompt   removes the grounding and abstention instructions.
                       Alone it changed declines (24 -> 0) and answer length,
                       but left the unsupported-claim rate flat at ~65%.

      OEM-only corpus  removes all OSHA/NIOSH material — 143 of 805 retrieved
                       chunk slots, 22 of 161 questions had an OSHA document
                       as their top match.

    The combination is the source-missing counterfactual from arXiv:2605.21949:
    keep the questions, take away the evidence, and see whether the model
    fabricates — and whether the trust layer catches it when it does.

    The original index at data/chroma is NOT touched. Every result produced so
    far stays comparable.
"""
from pathlib import Path

from src.rag.chunker import chunk_documents
from src.rag.loader import load_documents
from src.rag.retriever import build_vectorstore

OEM_MANUALS = {
    "KneeMill-Complete-Manual.pdf",                        # Bridgeport mill
    "english---lathe-ngc---operator_s-manual---2018.pdf",  # Haas TL-1 lathe
    "710-965-00_UR5e_User_Manual_en_Global.pdf",           # Universal Robots UR5e
}

OUT_DIR = "data/chroma_oem_only"


def main() -> None:
    docs = load_documents("data/raw")
    kept = [d for d in docs if d.metadata.get("source_file") in OEM_MANUALS]
    dropped = len(docs) - len(kept)

    print(f"\npages loaded   {len(docs)}")
    print(f"  kept (OEM)   {len(kept)}")
    print(f"  dropped      {dropped}   (OSHA / NIOSH / CFR)")

    from collections import Counter
    for name, n in Counter(d.metadata.get("source_file") for d in kept).most_common():
        print(f"    {n:>5}  {name}")

    chunks = chunk_documents(kept)
    build_vectorstore(chunks, persist_dir=OUT_DIR)
    print(f"\nOriginal index at data/chroma is untouched.")
    print("Next:")
    print(f"  python -m src.run_generation --chroma {OUT_DIR} --prompt minimal \\")
    print("      --out data/processed/generations_stress.jsonl")


if __name__ == "__main__":
    main()
