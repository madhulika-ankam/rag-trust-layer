#!/usr/bin/env python3
"""
build_perturbations.py — construct a labelled perturbation set for verifier
validation.

WHAT THIS PRODUCES
    A CSV where every row is a (claim, evidence, label) triple whose label is
    known with certainty, because we caused the error ourselves.

    Method follows BUMP (Ma et al., ACL 2023): take a text known to be
    faithful, make ONE minimal edit introducing ONE error, keep both versions.
    BUMP's stated purpose is diagnosing whether a metric is (1) consistent,
    (2) effective on human-written text, and (3) SENSITIVE TO DIFFERENT ERROR
    TYPES. That third property is why `perturbation_type` is on every row —
    the per-type breakdown is the differentiating result.

TWO SOURCES, DELIBERATELY
    corpus   A sentence lifted from a retrieved chunk. "Supported" is beyond
             dispute (the claim IS the evidence), and corrupting one value
             makes "unsupported" equally certain. High volume, clean labels,
             but LEXICALLY EASY — the positive shares every word with its
             evidence, which flatters the verifier.

    gold     A claim from an expert-validated gold answer, matched to its
             best supporting chunk. A paraphrase, not a copy. Realistic
             difficulty, low volume.

    Report them SEPARATELY. The gap between them is a difficulty gradient and
    an honest statement about how easy the synthetic set is — which is what
    Layer 0.6 of EVALUATION_PLAN.md exists to check.

WHY CORPUS-SOURCED AT ALL
    Only 14 of the 161 gold answers contain a number-with-unit or a
    regulatory code. Sourcing numerical perturbations from gold answers alone
    yields too few to measure anything. The corpus has 358 chunks with
    numeric values, 291 with regulatory codes, 189 with conditional language.

USAGE
    python -m src.build_perturbations --out data/processed/perturbations.csv
    python -m src.build_perturbations --per-type 10 --gold-limit 20   # trial
"""
from __future__ import annotations

import argparse
import csv
import random
import re
import sqlite3
from pathlib import Path

from src.rag.retriever import load_vectorstore, retrieve
from src.trust_layer.verifier import (
    _CODE_PATTERN,
    _NUMBER_PATTERN,
    _semantic_similarity,
)

CHROMA_DB = Path("data/chroma/chroma.sqlite3")

# Confidence that a retrieved chunk really supports a gold claim. Below this
# the row is emitted but flagged CHECK rather than OK.
SUPPORT_SIM_THRESHOLD = 0.55

MIN_SENT_CHARS = 40
MAX_SENT_CHARS = 300

_CONDITION_RE = re.compile(
    r"\s*\b(unless|except when|except where|except that|provided that|"
    r"other than when)\b.*$",
    re.IGNORECASE,
)

# review_status vocabulary — four values, each meaning exactly one thing.
#
#   OK      nothing to do.
#   TODO    the claim column is blank; you write it.
#   JUDGE   the row is complete but the LABEL is debatable; your call
#           whether to keep it as-is, reword it, or drop it.
#   CHECK   the row is DOUBTFUL and probably wrong; default action is delete.
#
# JUDGE and CHECK were originally one value, and a bulk "drop everything
# marked CHECK" swept away rows that only needed a decision. Keep them
# distinct: CHECK is safe to delete in bulk, JUDGE never is.
REVIEW_STATUSES = ("OK", "TODO", "JUDGE", "CHECK")

FIELDS = [
    "pair_id", "source", "perturbation_type", "claim", "original_claim",
    "what_changed", "label", "evidence", "evidence_source",
    "support_similarity", "split", "review_status", "notes",
]


# ───────────────────────────────── helpers ───────────────────────────────────


# PDF extraction flattens tables, parts lists, headers, footers and contents
# entries into text that superficially parses as a sentence. Perturbing those
# produces meaningless test items — changing a digit in a parts list is not a
# safety claim. These filters keep only things that read as prose.

_JUNK_PATTERNS = [
    re.compile(r"\.{4,}"),                        # contents dot-leaders
    re.compile(r"page\s+\d+\s+of\s+\d+", re.I),   # footers
    re.compile(r"\bfigure\s+[a-z0-9.\-]+", re.I), # figure references
    re.compile(r"\btable\s+[a-z0-9.\-]+\s", re.I),
    re.compile(r"(\b[A-Z0-9]{6,}\b.*){2,}"),      # part numbers in sequence
    re.compile(r"(\b\d[\d.,]*\b\s+){4,}"),        # runs of bare numbers
]

# A claim has to assert something. Require at least one of these.
_PREDICATE_RE = re.compile(
    r"\b(is|are|was|were|must|shall|should|can|may|will|has|have|requires?|"
    r"provides?|ensures?|prevents?|causes?|allows?|contains?|exceeds?|"
    r"do not|does not|be)\b",
    re.IGNORECASE,
)


def is_good_sentence(s: str) -> bool:
    if not (MIN_SENT_CHARS <= len(s) <= MAX_SENT_CHARS):
        return False
    digits = sum(c.isdigit() for c in s)
    letters = sum(c.isalpha() for c in s)
    if digits / len(s) > 0.20:          # tables and parts lists
        return False
    if letters / len(s) < 0.55:         # mostly punctuation or symbols
        return False
    if sum(c.isupper() for c in s) / max(letters, 1) > 0.5:   # headers
        return False
    if any(p.search(s) for p in _JUNK_PATTERNS):
        return False
    if not _PREDICATE_RE.search(s):     # not asserting anything
        return False
    return True


def sentences(text: str) -> list[str]:
    text = " ".join(text.split())
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if is_good_sentence(p.strip())]


def load_chunks() -> list[str]:
    """Read chunk text straight from the Chroma sqlite store."""
    con = sqlite3.connect(CHROMA_DB)
    rows = con.execute(
        "select string_value from embedding_metadata "
        "where key='chroma:document' and string_value is not null"
    ).fetchall()
    con.close()
    return [r[0] for r in rows]


# ───────────────────────────── the perturbations ─────────────────────────────


def perturb_number(claim: str, evidence: str) -> tuple[str, str] | None:
    """
    NUMERICAL — change one numeric value, keep its unit.

    Targets entity matching. An entailment model reads "200ms" and "500ms" as
    near-identical because the sentence structure is unchanged; exact matching
    does not. This is the perturbation type that should separate them.
    """
    match = _NUMBER_PATTERN.search(claim)
    if not match:
        return None
    original = match.group(0)
    digits = re.match(r"\d+(?:\.\d+)?", original)
    if not digits:
        return None

    value = float(digits.group(0))
    unit = original[digits.end():]

    for factor in (2.5, 0.4, 3.0, 0.25, 7.0):
        new_value = value * factor
        new_digits = (str(int(new_value)) if new_value == int(new_value)
                      else f"{new_value:.1f}")
        replacement = new_digits + unit
        # If the replacement already appears in the evidence, the
        # "unsupported" label would be wrong.
        if replacement.lower() in evidence.lower() or new_digits == digits.group(0):
            continue
        return (claim[:match.start()] + replacement + claim[match.end():],
                f"{original.strip()} -> {replacement.strip()}")
    return None


def perturb_code(claim: str, evidence: str) -> tuple[str, str] | None:
    """
    CODE SWAP — change a regulatory citation's digits.

    Targets entity matching via _CODE_PATTERN. "OSHA 1910.147" (lockout) and
    "OSHA 1910.212" (machine guarding) are different regulations; to an
    entailment model they are near-identical strings in identical contexts.
    """
    match = _CODE_PATTERN.search(claim)
    if not match:
        return None
    original = match.group(0)
    for a, b in (("147", "212"), ("212", "147"), ("178", "219"),
                 ("219", "178"), ("213", "215"), ("215", "213"),
                 ("217", "211"), ("211", "217")):
        if a not in original:
            continue
        replacement = original.replace(a, b, 1)
        if replacement.lower() in evidence.lower():
            continue
        return (claim[:match.start()] + replacement + claim[match.end():],
                f"{original} -> {replacement}")
    return None


def perturb_condition(claim: str, evidence: str) -> tuple[str, str] | None:
    """
    CONDITION DROPPED — remove a conditional exception the evidence states.

    "Lockout is required unless the equipment cannot be locked out."
        -> "Lockout is always required."

    This is the OMISSION category from CONTEXT.md, and the case
    _negation_check could not reach before the 2026-09-25 fix. The claim
    contains no negation marker of its own; only the evidence does.

    The condition is DROPPED but no absolute qualifier is inserted —
    automatic insertion produced broken grammar ("shall always not be
    tilted"). Every row of this type is flagged CHECK so you can add
    "always" / "in all cases" where it reads naturally.

    Note the label is genuinely debatable without that qualifier: evidence
    saying "required unless X" does still support "required" in the general
    case. It is the unconditional reading that is unsupported. Hardening the
    wording is what makes the label defensible.
    """
    match = _CONDITION_RE.search(claim)
    if not match:
        return None
    stripped = claim[:match.start()].strip().rstrip(",").rstrip()
    if len(stripped) < MIN_SENT_CHARS:
        return None
    if not stripped.endswith("."):
        stripped += "."
    return stripped, f"dropped condition: '{match.group(0).strip()[:70]}'"


PERTURBATIONS = [
    ("numerical", perturb_number, _NUMBER_PATTERN),
    ("code_swap", perturb_code, _CODE_PATTERN),
    ("condition_dropped", perturb_condition, _CONDITION_RE),
]


# ── types that need human judgement; templates are emitted, capped ───────────

HAND_WRITTEN = [
    ("negation_inverted",
     "Invert the claim's polarity against the evidence. evidence 'may remove "
     "the guard' -> claim 'may not remove the guard'. Tests the 0.4 branch of "
     "_negation_check (claim negates, evidence does not)."),
    ("term_swap",
     "Swap a named thing for a plausible wrong one: 'Recovery mode' -> "
     "'Emergency mode'. NOTE: entity matching CANNOT catch these — it only "
     "sees numbers-with-units and regulatory codes. Only NLI can. That is "
     "exactly why they belong in the set."),
    ("unsupported_addition",
     "Add a specific detail appearing nowhere in the evidence. Extrinsic "
     "hallucination — what Llama 3 actually did in Q48."),
]


# ──────────────────────────────── build ──────────────────────────────────────


def build_corpus_rows(chunks, per_type, rng):
    """One minimal pair per selected sentence: the sentence, and a corruption."""
    rows = []
    for ptype, fn, pattern in PERTURBATIONS:
        candidates = [c for c in chunks if pattern.search(c)]
        rng.shuffle(candidates)
        made = 0
        for chunk in candidates:
            if made >= per_type:
                break
            evidence = " ".join(chunk.split())
            for sent in sentences(chunk):
                if not pattern.search(sent):
                    continue
                result = fn(sent, evidence)
                if not result:
                    continue
                corrupted, changed = result
                rows.append(("corpus", "none", sent, sent, "", "supported",
                             evidence, "corpus chunk", "", "OK", ""))
                # condition_dropped gets JUDGE, not CHECK: the label is
                # debatable (evidence saying "required unless X" does still
                # support "required" in the general case), but the row is
                # sound. It needs a decision, not deletion.
                rows.append(("corpus", ptype, corrupted, sent, changed,
                             "unsupported", evidence, "corpus chunk", "",
                             "OK" if ptype != "condition_dropped" else "JUDGE",
                             "" if ptype != "condition_dropped"
                             else "omission: harden the wording (add 'always' / "
                                  "'in all cases') so the overstatement is explicit, "
                                  "then set OK"))
                made += 1
                break
    return rows


def build_gold_rows(qa_rows, vectorstore, k, limit):
    """Gold-answer claims paired with their best supporting chunk."""
    rows = []
    for row in qa_rows[:limit] if limit else qa_rows:
        question = (row.get("question") or "").strip()
        gold = (row.get("gold_answer") or "").strip()
        if not question or not gold:
            continue
        chunks = retrieve(question, vectorstore, k=k)
        if not chunks:
            continue

        # No fallback to the raw gold answer. An earlier version fell back to
        # `[gold.strip()]` when the quality filter rejected everything, which
        # reintroduced exactly what the filter exists to remove — numbered
        # procedures ("1. Remove the motor. 2. Lower the quill..."), bare
        # fragments ("314, 336 and 333 respectively"), and answers that are
        # only meaningful beside their question ("At least weekly").
        # 39 of the 161 gold answers yield no self-contained claim. Skip them.
        for claim in sentences(gold):
            scored = [(_semantic_similarity(claim, c.page_content), c) for c in chunks]
            sim, best = max(scored, key=lambda t: t[0])
            evidence = " ".join(best.page_content.split())
            source = (f"{best.metadata.get('source_file', 'unknown')} "
                      f"p.{best.metadata.get('page', '?')}")

            ok = sim >= SUPPORT_SIM_THRESHOLD
            rows.append(("gold", "none", claim, claim, "", "supported",
                         evidence, source, round(sim, 4),
                         "OK" if ok else "CHECK",
                         "" if ok else "low similarity — confirm this chunk supports the claim, or drop"))

            for ptype, fn, _pattern in PERTURBATIONS:
                result = fn(claim, evidence)
                if result:
                    corrupted, changed = result
                    rows.append(("gold", ptype, corrupted, claim, changed,
                                 "unsupported", evidence, source, round(sim, 4),
                                 "OK", ""))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--qa", type=Path, default=Path("data/processed/qa_pairs_labeled.csv"))
    ap.add_argument("--out", type=Path, default=Path("data/processed/perturbations.csv"))
    ap.add_argument("--per-type", type=int, default=35,
                    help="corpus-sourced pairs per automated perturbation type")
    ap.add_argument("--templates", type=int, default=15,
                    help="blank rows per hand-written type")
    ap.add_argument("--gold-limit", type=int, default=0, help="0 = all questions")
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rng = random.Random(args.seed)

    print("Reading corpus chunks...")
    chunks = load_chunks()
    print(f"  {len(chunks)} chunks")

    print("Building corpus-sourced pairs...")
    raw = build_corpus_rows(chunks, args.per_type, rng)

    print("Loading vector store (for gold-answer pairs)...")
    vectorstore = load_vectorstore()
    print("Building gold-answer pairs...")
    raw += build_gold_rows(args.qa and list(csv.DictReader(args.qa.open(encoding="utf-8"))),
                           vectorstore, args.k, args.gold_limit)

    # Templates for the judgement-based types — PRE-FILLED with real evidence
    # and a real source sentence, so the only thing left to do is write the
    # corrupted claim. Hunting for source material is the slow part; this
    # removes it.
    prose = []
    for chunk in chunks:
        for sent in sentences(chunk):
            prose.append((sent, " ".join(chunk.split())))
    rng.shuffle(prose)

    cursor = 0
    for ptype, guidance in HAND_WRITTEN:
        for _ in range(args.templates):
            if cursor >= len(prose):
                break
            sent, evidence = prose[cursor]
            cursor += 1
            # The unmodified sentence is a free positive; keep it.
            raw.append(("template", "none", sent, sent, "", "supported",
                        evidence, "corpus chunk", "", "OK", ""))
            # And the row for you to fill in.
            raw.append(("template", ptype, "", sent, "", "unsupported",
                        evidence, "corpus chunk", "", "TODO", guidance))

    # Assign splits by ORIGINAL claim, so a pair and its twin never separate.
    split_of: dict[str, str] = {}
    out = []
    for i, (src, ptype, claim, original, changed, label, ev, evsrc, sim, status, note) in enumerate(raw, 1):
        key = original or f"template-{i}"
        if key not in split_of:
            split_of[key] = "validation" if rng.random() < 0.5 else "test"
        out.append({
            "pair_id": i, "source": src, "perturbation_type": ptype,
            "claim": claim, "original_claim": original, "what_changed": changed,
            "label": label, "evidence": ev, "evidence_source": evsrc,
            "support_similarity": sim, "split": split_of[key],
            "review_status": status, "notes": note,
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(out)

    from collections import Counter
    print(f"\nWrote {len(out)} rows to {args.out}\n")
    for title, counter in (
        ("source", Counter(r["source"] for r in out)),
        ("perturbation_type", Counter(r["perturbation_type"] for r in out)),
        ("label", Counter(r["label"] for r in out)),
        ("review_status", Counter(r["review_status"] for r in out)),
        ("split", Counter(r["split"] for r in out)),
    ):
        print(f"by {title}:")
        for name, count in counter.most_common():
            print(f"  {name:<26} {count:>5}")
        print()

    print("Next:")
    print("  1. review_status=CHECK  — confirm the evidence supports the claim.")
    print("     A wrong positive is worse than no positive. Fix or delete.")
    print("  2. review_status=TODO   — write the claim by hand, or delete the row.")
    print("     You do not need all of them; 10-15 per type is plenty.")
    print("  3. Spot-check the automated corruptions: is the corrupted value")
    print("     genuinely absent from the evidence?")
    print("  4. Set review_status=OK on everything you keep.")


if __name__ == "__main__":
    main()
