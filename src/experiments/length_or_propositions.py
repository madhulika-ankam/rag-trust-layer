#!/usr/bin/env python3
"""
length_or_propositions.py — is it the LENGTH of a claim that breaks NLI, or
the number of separate propositions packed into it?

WHY THIS MATTERS
    These give different design rules. "Keep claims short" is a word budget.
    "Keep claims to one proposition" is a parse-level rule, and a 30-word
    single proposition would be fine under it.

    The question surfaced from granularity_by_length.py. On the perturbation
    set, where every claim is a single proposition lifted from a manual,
    mean entailment on supported pairs does NOT fall with length at sentence
    granularity (0.868 at under 15 words, 0.911 at 30+). On real decomposed
    claims it collapses (0.675 under 12 words, 0.329 at 20+). The two
    populations differ in composition, not just in length: a long REAL claim
    is long because it bundles several facts.

HOW
    Count clauses in each real claim with the spaCy parse already loaded by
    the decomposer — a clause head is a ROOT, or a conjoined / complement /
    adverbial / relative clause verb. Then hold one variable fixed and vary
    the other.

USAGE
    venv/bin/python src/experiments/length_or_propositions.py
"""
from __future__ import annotations

import json
import statistics as st
import sys

sys.path.insert(0, ".")
from src.trust_layer.decomposer import _get_nlp

CLAUSE_DEPS = {"ROOT", "conj", "ccomp", "xcomp", "advcl", "relcl", "acl", "pcomp"}


def clauses(doc) -> int:
    return max(1, sum(1 for t in doc
                      if t.dep_ in CLAUSE_DEPS and t.pos_ in {"VERB", "AUX"}))


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else "data/processed/verified.jsonl"
    recs = [json.loads(l) for l in open(path, encoding="utf-8")]
    nlp = _get_nlp()
    claims = []
    for r in recs:
        for c in r["claims"]:
            doc = nlp(c["claim"])
            claims.append({"w": len(c["claim"].split()), "c": clauses(doc),
                           "e": c["entailment_p"],
                           "sup": c["verdict"] == "SUPPORTED"})

    print(f"  {len(claims)} real claims from {path}\n")

    print("  A. HOLD PROPOSITIONS AT ONE, VARY LENGTH")
    print("     If length is the cause, entailment should still fall here.\n")
    print(f"     {'claim words':<14}{'n':>5}{'mean entail':>13}{'% SUPPORTED':>14}")
    print("     " + "-" * 46)
    single = [c for c in claims if c["c"] == 1]
    for lo, hi in [(0, 10), (10, 15), (15, 20), (20, 999)]:
        g = [c for c in single if lo <= c["w"] < hi]
        if len(g) < 8:
            continue
        label = f"{lo}-{hi}" if hi < 999 else f"{lo}+"
        print(f"     {label:<14}{len(g):>5}{st.mean(c['e'] for c in g):>13.3f}"
              f"{sum(c['sup'] for c in g) / len(g) * 100:>13.0f}%")

    print("\n  B. HOLD LENGTH ROUGHLY FIXED, VARY PROPOSITIONS")
    print("     If propositions are the cause, entailment should fall here.\n")
    for lo, hi in [(12, 20), (20, 999)]:
        band = [c for c in claims if lo <= c["w"] < hi]
        label = f"{lo}-{hi} words" if hi < 999 else f"{lo}+ words"
        print(f"     {label}  (n={len(band)})")
        print(f"       {'clauses':<10}{'n':>5}{'mean entail':>13}{'% SUPPORTED':>14}")
        for lo_c, hi_c in [(1, 2), (2, 3), (3, 99)]:
            g = [c for c in band if lo_c <= c["c"] < hi_c]
            if len(g) < 8:
                continue
            tag = f"{lo_c}" if hi_c - lo_c == 1 else f"{lo_c}+"
            print(f"       {tag:<10}{len(g):>5}{st.mean(c['e'] for c in g):>13.3f}"
                  f"{sum(c['sup'] for c in g) / len(g) * 100:>13.0f}%")
        print()

    try:
        from scipy.stats import spearmanr
        w = [c["w"] for c in claims]; cl = [c["c"] for c in claims]
        e = [c["e"] for c in claims]
        print("  C. CORRELATIONS over all claims")
        for name, x in (("length   vs entailment", w), ("clauses  vs entailment", cl)):
            rho, p = spearmanr(x, e)
            print(f"     {name} : rho {rho:+.3f}  p {p:.2e}")
        rho, p = spearmanr(w, cl)
        print(f"     length   vs clauses    : rho {rho:+.3f}  p {p:.2e}")
        print("     (the two predictors are correlated, so these do not")
        print("      separate the causes on their own — A and B do)")
    except ImportError:
        print("  (scipy not installed — correlations skipped)")


if __name__ == "__main__":
    main()
