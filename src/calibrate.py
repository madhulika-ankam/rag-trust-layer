#!/usr/bin/env python3
"""
calibrate.py — select the aggregator and the decision thresholds, instead of
choosing them.

THE PROBLEM THIS SOLVES
    ANSWER = 0.85 and WARN = 0.60 were typed into decision.py. Nothing
    produced them. That is the whole of Dr. Maier's objection: a score of
    0.548 has no external meaning, and neither does a threshold picked to sit
    near it.

THE METHOD
    State a risk tolerance FIRST, then take the configuration that maximises
    coverage while staying under it, selected on the VALIDATION split and
    reported on TEST. The judgement then lives in the tolerance — a domain
    argument about manufacturing safety that can be defended in words — not
    in the number.

    This is the selective-prediction / risk-coverage framework
    (El-Yaniv & Wiener 2010; Geifman & El-Yaniv 2017), and the sweep follows
    SABER (arXiv:2605.18792), which reports coverage and risk-on-answered
    across a threshold sweep.

TWO THRESHOLDS, SWEPT INDEPENDENTLY
    An earlier version tied WARN = ANSWER - 0.25, so "coverage" was really
    driven by WARN alone and the ANSWER sweep was reporting the wrong thing.
    Both are swept here, subject only to WARN <= ANSWER.

THE RISK AXIS IS A PROXY
    A true unsupported-answer delivery rate needs human judgement of each
    delivered answer; only 30 such labels exist. Risk here is "delivered an
    answer to a question the label says should be ESCALATE/REFUSE", which
    needs no new labelling but is NOT the headline metric. Those labels are
    themselves regex-generated (see CONTEXT.md section D item 0). Report the
    axis honestly.

USAGE
    python -m src.calibrate
    python -m src.calibrate --tolerance 0.10
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from src.trust_layer.scorer import _aggregate

DELIVERED = ("ANSWER", "WARN")
WITHHOLD_EXPECTED = ("REFUSE", "ESCALATE")
AGGREGATORS = ("current", "proportion", "min")


def agg(claims, rule):
    return _aggregate([c["combined"] for c in claims],
                      [c["verdict"] for c in claims], rule)


def decide(score, claims, answer_t, warn_t):
    if not claims:
        return "REFUSE"
    if any(c["verdict"] == "CONTRADICTION" for c in claims):
        return "ESCALATE"
    if score >= answer_t:
        return "ANSWER"
    if score >= warn_t:
        return "WARN"
    return "REFUSE"


def measure(recs, rule, answer_t, warn_t):
    dec = [decide(agg(r["claims"], rule), r["claims"], answer_t, warn_t) for r in recs]
    delivered = [d in DELIVERED for d in dec]
    n_del = sum(delivered)
    risky = sum(1 for d, r in zip(dec, recs)
                if d in DELIVERED and r["expected_decision"] in WITHHOLD_EXPECTED)
    answerable = sum(1 for r in recs if r["expected_decision"] == "ANSWER")
    over = sum(1 for d, r in zip(dec, recs)
               if d not in DELIVERED and r["expected_decision"] == "ANSWER")
    acc = sum(1 for d, r in zip(dec, recs) if d == r["expected_decision"]) / len(recs)
    return {
        "coverage": n_del / len(recs),
        "risk": risky / n_del if n_del else 0.0,
        "over_abstention": over / answerable if answerable else 0.0,
        "accuracy": acc,
        "delivered": n_del,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verified", type=Path,
                    default=Path("data/processed/verified.jsonl"))
    ap.add_argument("--tolerance", type=float, default=None,
                    help="max acceptable risk; omit to see several")
    args = ap.parse_args()

    recs = [json.loads(l) for l in args.verified.open(encoding="utf-8")]

    # Stratified by expected_decision so both halves carry a similar mix,
    # rather than splitting on question_id parity.
    val, test, seen = [], [], Counter()
    for r in sorted(recs, key=lambda x: (x["expected_decision"], x["question_id"])):
        k = r["expected_decision"]
        (val if seen[k] % 2 == 0 else test).append(r)
        seen[k] += 1

    print(f"validation {len(val)}  test {len(test)}   (stratified by expected_decision)")
    print(f"  val  {dict(Counter(r['expected_decision'] for r in val))}")
    print(f"  test {dict(Counter(r['expected_decision'] for r in test))}")

    grid = [round(x / 20, 2) for x in range(1, 20)]
    tolerances = [args.tolerance] if args.tolerance else [0.05, 0.10, 0.15, 0.20, 0.30]

    print("\n" + "=" * 78)
    print("SELECTED ON VALIDATION, REPORTED ON TEST")
    print("=" * 78)
    print(f"  {'tol':>5}{'rule':<13}{'ANS':>6}{'WARN':>6}"
          f"{'cov(val)':>10}{'risk(val)':>11}{'cov(TEST)':>11}{'risk(TEST)':>12}")
    print('  ' + '-' * 74)

    for tol in tolerances:
        best = None
        for rule in AGGREGATORS:
            for a in grid:
                for w in grid:
                    if w > a:
                        continue
                    m = measure(val, rule, a, w)
                    if m["risk"] <= tol and (best is None or m["coverage"] > best[0]["coverage"]):
                        best = (m, rule, a, w)
        if best is None:
            print(f"  {tol:>5.2f}  no configuration meets this tolerance")
            continue
        m, rule, a, w = best
        t = measure(test, rule, a, w)
        print(f"  {tol:>5.2f}{rule:<13}{a:>6.2f}{w:>6.2f}"
              f"{m['coverage']*100:>9.1f}%{m['risk']*100:>10.1f}%"
              f"{t['coverage']*100:>10.1f}%{t['risk']*100:>11.1f}%")

    print("\n  Read a row as: 'at a stated tolerance of X, the configuration")
    print("  maximising coverage on validation is <rule> at <ANS>/<WARN>,")
    print("  and on held-out test data it delivers <cov> at <risk>.'")
    print("\n  The thresholds are then DERIVED. Your judgement sits in the")
    print("  tolerance, which is a domain argument, not in the numbers.")

    print("\n" + "=" * 78)
    print("CURRENT SETTINGS, for comparison   (ANSWER 0.85 / WARN 0.60)")
    print("=" * 78)
    print(f"  {'rule':<13}{'cov(TEST)':>11}{'risk(TEST)':>12}{'over-abst':>12}{'dec.acc':>10}")
    for rule in AGGREGATORS:
        t = measure(test, rule, 0.85, 0.60)
        print(f"  {rule:<13}{t['coverage']*100:>10.1f}%{t['risk']*100:>11.1f}%"
              f"{t['over_abstention']*100:>11.1f}%{t['accuracy']*100:>9.1f}%")
    print()


if __name__ == "__main__":
    main()
