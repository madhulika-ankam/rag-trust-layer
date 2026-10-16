#!/usr/bin/env python3
"""
evaluate_system.py — answer-level evaluation.

evaluate_verifier.py answered "is my verifier any good?" against the
perturbation set. This answers the other four metric groups: is the SYSTEM
any good?

    coverage, over-abstention        Group 3
    decision accuracy, per-class     Group 5
    risk-coverage curve              Group 3  <- the answer to "on what
                                                 basis are these numbers?"
    cost and latency                 Group 1

AGGREGATORS COMPARED
    current      mean(scores) x (1 - bad_fraction)
                 Your scorer.py. No published precedent, and it penalises a
                 bad claim TWICE — once through the mean, once through the
                 penalty factor. With one bad claim of n the score cannot
                 exceed 1 - 1/n, so ANSWER (>=0.85) is unreachable at the
                 2-4 claims a typical answer produces.

    proportion   supported / total
                 This is RAGAS faithfulness: "the proportion of claims in a
                 response that can be inferred from the context". Citable,
                 and it is already exactly your penalty_factor.

    min          min(claim scores)
                 SummaC-ZS style: the weakest claim determines the answer.
                 Conservative, which suits a safety component.

RISK PROXY - read this before quoting any number below
    A true unsupported-answer delivery rate needs a human judgement of
    whether each DELIVERED answer contained an unsupported claim. Those
    labels do not exist yet, and using the trust layer's own verdicts would
    be grading your own homework.

    So risk here is proxied by the expected_decision labels: a risk event is
    delivering an answer to a question a domain expert marked ESCALATE or
    REFUSE. That is a genuine risk event and it needs no new labelling, but
    it is NOT the headline metric from EVALUATION_PLAN.md Layer 3. Label the
    axis honestly in the thesis.

USAGE
    python -m src.evaluate_system
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from src.trust_layer.decision import ANSWER_THRESHOLD, WARN_THRESHOLD

DELIVERED = ("ANSWER", "WARN")
SHOULD_NOT_DELIVER = ("REFUSE", "ESCALATE")


# ───────────────────────────── aggregators ──────────────────────────────────

def agg_current(claims):
    if not claims:
        return 0.0
    scores = [c["combined"] for c in claims]
    bad = sum(1 for c in claims if c["verdict"] in ("UNSUPPORTED", "CONTRADICTION"))
    return (sum(scores) / len(scores)) * (1 - bad / len(claims))


def agg_proportion(claims):
    if not claims:
        return 0.0
    good = sum(1 for c in claims if c["verdict"] == "SUPPORTED")
    return good / len(claims)


def agg_min(claims):
    return min((c["combined"] for c in claims), default=0.0)


AGGREGATORS = [
    ("current  mean x (1-bad)", agg_current),
    ("proportion  (RAGAS)", agg_proportion),
    ("min  (SummaC-ZS)", agg_min),
]


def decide_from(score, claims, answer_t, warn_t):
    if not claims:
        return "REFUSE"
    if any(c["verdict"] == "CONTRADICTION" for c in claims):
        return "ESCALATE"
    if score >= answer_t:
        return "ANSWER"
    if score >= warn_t:
        return "WARN"
    return "REFUSE"


def banner(t):
    print("\n" + "=" * 76); print(t); print("=" * 76)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verified", type=Path,
                    default=Path("data/processed/verified.jsonl"))
    args = ap.parse_args()

    recs = [json.loads(l) for l in args.verified.open(encoding="utf-8")]
    val = [r for r in recs if r["question_id"] % 2 == 0]
    test = [r for r in recs if r["question_id"] % 2 == 1]

    banner("DATASET")
    print(f"  questions              {len(recs)}")
    print(f"  validation / test      {len(val)} / {len(test)}   (by question_id parity)")
    print(f"  expected_decision      {dict(Counter(r['expected_decision'] for r in recs))}")
    print(f"  declined to answer     {sum(1 for r in recs if r['declined_to_answer'])}")
    print(f"  claims per answer      {dict(sorted(Counter(len(r['claims']) for r in recs).items()))}")

    banner("1. COST AND LATENCY   (Group 1 - comparable to Singh et al.)")
    gen = [r["generation_ms"] for r in recs]
    ret = [r["retrieval_ms"] for r in recs]
    print(f"  retrieval   mean {sum(ret)/len(ret)/1000:6.2f}s")
    print(f"  generation  mean {sum(gen)/len(gen)/1000:6.2f}s")
    print(f"  end-to-end  mean {(sum(ret)+sum(gen))/len(recs)/1000:6.2f}s")
    print(f"  cost per query   $0.00   (local inference, no API)")
    print(f"\n  Singh et al. (arXiv:2511.11847): 86.66% accuracy, $0.005/query, 10.04s")

    banner("2. AGGREGATOR COMPARISON   (at the current thresholds "
           f"{ANSWER_THRESHOLD}/{WARN_THRESHOLD})")
    print(f"  {'aggregator':<26}{'coverage':>10}{'risk':>8}{'over-abst':>11}{'dec.acc':>9}")
    print("  " + "-" * 64)
    for name, fn in AGGREGATORS:
        dec = [decide_from(fn(r["claims"]), r["claims"],
                           ANSWER_THRESHOLD, WARN_THRESHOLD) for r in recs]
        delivered = [d in DELIVERED for d in dec]
        cov = sum(delivered) / len(recs)
        risky = [d for d, r in zip(dec, recs)
                 if d in DELIVERED and r["expected_decision"] in SHOULD_NOT_DELIVER]
        risk = len(risky) / max(sum(delivered), 1)
        over = sum(1 for d, r in zip(dec, recs)
                   if d not in DELIVERED and r["expected_decision"] == "ANSWER")
        answerable = sum(1 for r in recs if r["expected_decision"] == "ANSWER")
        acc = sum(1 for d, r in zip(dec, recs) if d == r["expected_decision"]) / len(recs)
        print(f"  {name:<26}{cov*100:>9.1f}%{risk*100:>7.1f}%"
              f"{over/max(answerable,1)*100:>10.1f}%{acc*100:>8.1f}%")
    print("\n  risk = of answers DELIVERED, the fraction the expert marked")
    print("         ESCALATE/REFUSE. A proxy - see the module docstring.")
    print("  over-abstention = of questions the expert marked ANSWER, the")
    print("         fraction the system withheld.")

    banner("3. RISK-COVERAGE   (sweep the ANSWER threshold)")
    for name, fn in AGGREGATORS:
        print(f"\n  {name}")
        print(f"    {'threshold':>10}{'coverage':>11}{'risk':>8}{'delivered':>11}")
        for t in (0.9, 0.85, 0.75, 0.65, 0.55, 0.45, 0.35, 0.25):
            dec = [decide_from(fn(r["claims"]), r["claims"], t, max(t - 0.25, 0.05))
                   for r in recs]
            d = [x in DELIVERED for x in dec]
            n = sum(d)
            risky = sum(1 for x, r in zip(dec, recs)
                        if x in DELIVERED and r["expected_decision"] in SHOULD_NOT_DELIVER)
            print(f"    {t:>10.2f}{n/len(recs)*100:>10.1f}%"
                  f"{(risky/max(n,1))*100:>7.1f}%{n:>11}")
    print("\n  State a risk tolerance, then read off the threshold that")
    print("  maximises coverage while staying under it. The threshold is")
    print("  then derived rather than chosen.")

    banner("4. DECISION ACCURACY   (Group 5, current aggregator)")
    dec = [decide_from(agg_current(r["claims"]), r["claims"],
                       ANSWER_THRESHOLD, WARN_THRESHOLD) for r in recs]
    labels = ["ANSWER", "WARN", "REFUSE", "ESCALATE"]
    cm = defaultdict(Counter)
    for d, r in zip(dec, recs):
        cm[r["expected_decision"]][d] += 1
    print(f"    {'expected \\\\ actual':<20}" + "".join(f"{l:>10}" for l in labels))
    for e in labels:
        if not cm[e]:
            continue
        print(f"    {e:<20}" + "".join(f"{cm[e][a]:>10}" for a in labels))
    print()
    for l in labels:
        tp = cm[l][l]
        fp = sum(cm[e][l] for e in labels if e != l)
        fn_ = sum(cm[l][a] for a in labels if a != l)
        if tp + fp + fn_ == 0:
            continue
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn_) if tp + fn_ else 0.0
        star = "   <- recall matters more than precision here" if l == "ESCALATE" else ""
        print(f"    {l:<12} precision {prec:.3f}   recall {rec:.3f}{star}")
    print()


if __name__ == "__main__":
    main()
