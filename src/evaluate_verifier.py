#!/usr/bin/env python3
"""
evaluate_verifier.py — verifier validation against the perturbation set.

Reads the raw mechanism features produced by extract_features.py and reports
everything needed for the verifier-validation section of the thesis. No model
is loaded; every table below is computed from stored features, so comparing
five combination rules costs seconds rather than five full runs.

WHAT IT REPORTS

  1. COMBINATION RULES
     Five ways of combining the mechanisms, including one with the weights
     FITTED rather than chosen. This is the direct answer to "the 0.30 / 0.70
     weighting is arbitrary" — the weighting stops being a preference and
     becomes a row in a table.

  2. PER-PERTURBATION-TYPE DETECTION
     Accuracy pooled across error types hides the effect this thesis claims.
     Entity matching should dominate on numerical and code errors and do
     nothing elsewhere; negation detection should show up only on dropped
     conditions. BUMP (Ma et al., ACL 2023) makes sensitivity to different
     error types an explicit design goal for exactly this reason.

  3. ABLATION
     Cumulative, in pipeline order. Doubles as an integration test: if adding
     a mechanism changes nothing, it is not wired in — a bug, not a finding.

  4. CONDITION_DROPPED SPLIT BY NEGATION MARKER
     Claims carrying a marker of their own route to a branch where the
     negation mechanism structurally cannot fire. Reported separately so the
     two cases are not conflated.

METHOD
  Thresholds are selected on the VALIDATION split at the point maximising
  balanced accuracy — equivalent to maximising Youden's J, since
  balanced accuracy = (J + 1) / 2 — and applied unchanged to TEST.
  Balanced accuracy is SummaC's primary metric; ROC-AUC is threshold-free
  and is the example-level metric argued for by TRUE.

USAGE
    python -m src.evaluate_verifier
    python -m src.evaluate_verifier --csv results.csv    # also write tables
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, roc_auc_score

from src.trust_layer.verifier import CONTRADICTION_THRESH

FEATURE_NAMES = ["entailment_p", "similarity", "entity_score",
                 "negation_score", "contradiction_p"]


# ─────────────────────────────── loading ─────────────────────────────────────


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))

    for r in rows:
        # Rows that failed the similarity gate have no NLI output. Fill with
        # the values that reproduce what the pipeline actually does: no
        # support, no contradiction, no penalties.
        gated = r["gate_passed"] == "1"
        r["gated"] = gated
        r["similarity"] = float(r["similarity"])
        r["entailment_p"] = float(r["entailment_p"]) if gated else 0.0
        r["contradiction_p"] = float(r["contradiction_p"]) if gated else 0.0
        r["entity_score"] = float(r["entity_score"]) if r["entity_score"] else 1.0
        r["negation_score"] = float(r["negation_score"]) if r["negation_score"] else 1.0
        r["y"] = 1 if r["label"] == "supported" else 0
    return rows


# ───────────────────────────── combination rules ─────────────────────────────
# Each returns a support score in [0, 1]. Higher = more supported.
# The contradiction override and the similarity gate are part of the pipeline
# rather than part of the blend, so they apply identically to every rule.


def _penalties(r: dict) -> float:
    return r["entity_score"] * r["negation_score"]


def _guard(r: dict, value: float) -> float:
    if r["gated"] is False:
        return 0.0                      # chunk never passed the gate
    if r["contradiction_p"] > CONTRADICTION_THRESH:
        return 0.0                      # contradiction overrides
    return value


def rule_entailment_only(r):
    return _guard(r, r["entailment_p"] * _penalties(r))


def rule_equal(r):
    return _guard(r, (0.5 * r["similarity"] + 0.5 * r["entailment_p"]) * _penalties(r))


def rule_current(r):
    return _guard(r, (0.30 * r["similarity"] + 0.70 * r["entailment_p"]) * _penalties(r))


def rule_similarity_heavy(r):
    return _guard(r, (0.70 * r["similarity"] + 0.30 * r["entailment_p"]) * _penalties(r))


COMBINATION_RULES = [
    ("entailment only", rule_entailment_only),
    ("0.5 sim + 0.5 entail", rule_equal),
    ("0.3 sim + 0.7 entail (current)", rule_current),
    ("0.7 sim + 0.3 entail", rule_similarity_heavy),
]

# Cumulative ablation, in the pipeline's own order.
ABLATION = [
    ("NLI only", lambda r: _guard(r, r["entailment_p"])),
    ("+ similarity", lambda r: _guard(r, 0.30 * r["similarity"] + 0.70 * r["entailment_p"])),
    ("+ entity", lambda r: _guard(r, (0.30 * r["similarity"] + 0.70 * r["entailment_p"])
                                 * r["entity_score"])),
    ("+ negation (full)", rule_current),
]


# ─────────────────────────────── evaluation ──────────────────────────────────


def pick_threshold(scores, y) -> tuple[float, float]:
    """
    Threshold maximising balanced accuracy on the given data.

    Equivalent to maximising Youden's J (J = sensitivity + specificity - 1),
    since balanced accuracy = (J + 1) / 2. Youden's J is the standard way of
    selecting an operating point from an ROC curve.
    """
    best_t, best_ba = 0.5, -1.0
    for t in sorted(set(np.round(scores, 4))) + [1.01]:
        ba = balanced_accuracy_score(y, [1 if s >= t else 0 for s in scores])
        if ba > best_ba:
            best_ba, best_t = ba, float(t)
    return best_t, best_ba


def auc(y, scores) -> float | None:
    return roc_auc_score(y, scores) if len(set(y)) > 1 else None


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """
    Wilson score interval for a proportion.

    Reported because the per-type cells are small: at n=7 a single item moves
    the rate by 14 points, so a bare percentage implies precision the sample
    cannot support. Cells below roughly 20 are indicative only.
    """
    import math
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def fmt(x, nd=4):
    return "   n/a" if x is None else f"{x:.{nd}f}"


def evaluate(rows, score_fn):
    """Select the threshold on validation, report on test."""
    val = [r for r in rows if r["split"] == "validation"]
    test = [r for r in rows if r["split"] == "test"]

    sv = [score_fn(r) for r in val]
    st = [score_fn(r) for r in test]
    yv = [r["y"] for r in val]
    yt = [r["y"] for r in test]

    t, ba_val = pick_threshold(sv, yv)
    pred = [1 if s >= t else 0 for s in st]
    return {
        "threshold": t,
        "ba_val": ba_val,
        "ba_test": balanced_accuracy_score(yt, pred),
        "auc_test": auc(yt, st),
        "test_rows": test,
        "test_scores": st,
        "test_pred": pred,
    }


def fit_logistic(rows):
    """
    Weights fitted by maximum likelihood on the validation split.

    This is what converts "why 0.30 and 0.70?" from a preference into an
    estimate: the coefficients are the values that maximise the likelihood of
    the observed labels, computed by a standard method. It also handles the
    fact that the mechanisms are on incommensurable scales — a cosine and a
    softmax probability are not the same kind of quantity, and the fitted
    coefficient is the exchange rate between them.
    """
    val = [r for r in rows if r["split"] == "validation"]
    test = [r for r in rows if r["split"] == "test"]
    Xv = np.array([[r[f] for f in FEATURE_NAMES] for r in val])
    Xt = np.array([[r[f] for f in FEATURE_NAMES] for r in test])
    yv = np.array([r["y"] for r in val])
    yt = np.array([r["y"] for r in test])

    model = LogisticRegression(max_iter=2000)
    model.fit(Xv, yv)
    st = model.predict_proba(Xt)[:, 1]
    sv = model.predict_proba(Xv)[:, 1]

    t, ba_val = pick_threshold(sv, yv)
    pred = [1 if s >= t else 0 for s in st]
    return {
        "threshold": t, "ba_val": ba_val,
        "ba_test": balanced_accuracy_score(yt, pred),
        "auc_test": auc(list(yt), list(st)),
        "coefficients": dict(zip(FEATURE_NAMES, model.coef_[0].round(4))),
        "intercept": round(float(model.intercept_[0]), 4),
        "test_rows": test, "test_scores": list(st), "test_pred": pred,
    }


def per_type(result):
    """Detection rate per perturbation type, plus recall on the positives."""
    out = {}
    buckets = defaultdict(lambda: [0, 0])
    for r, p in zip(result["test_rows"], result["test_pred"]):
        if r["y"] == 1:
            key = "SUPPORTED (controls)"
            buckets[key][1] += 1
            buckets[key][0] += 1 if p == 1 else 0        # correctly kept
        else:
            key = r["perturbation_type"]
            buckets[key][1] += 1
            buckets[key][0] += 1 if p == 0 else 0        # correctly rejected
    for k, (hit, n) in buckets.items():
        out[k] = (hit, n, hit / n if n else 0.0)
    return out


# ──────────────────────────────── reporting ──────────────────────────────────


def banner(title):
    print("\n" + "=" * 74)
    print(title)
    print("=" * 74)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", type=Path,
                    default=Path("data/processed/features.csv"))
    ap.add_argument("--csv", type=Path, default=None,
                    help="also write the tables to this CSV")
    args = ap.parse_args()

    rows = load(args.features)
    val = sum(1 for r in rows if r["split"] == "validation")
    test = sum(1 for r in rows if r["split"] == "test")

    banner("DATASET")
    print(f"  rows            {len(rows)}")
    print(f"  validation      {val}   (thresholds and weights selected here)")
    print(f"  test            {test}   (reported here, touched once)")
    print(f"  labels          {dict(Counter(r['label'] for r in rows))}")
    gated = sum(1 for r in rows if not r["gated"])
    print(f"  failed the similarity gate: {gated}")

    # ── 1. combination rules ────────────────────────────────────────────────
    banner("1. COMBINATION RULES   (threshold chosen on validation)")
    print(f"  {'rule':<34}{'thresh':>8}{'BA val':>9}{'BA test':>9}{'AUC test':>10}")
    print("  " + "-" * 70)
    results = {}
    for name, fn in COMBINATION_RULES:
        res = evaluate(rows, fn)
        results[name] = res
        print(f"  {name:<34}{res['threshold']:>8.3f}{res['ba_val']:>9.4f}"
              f"{res['ba_test']:>9.4f}{fmt(res['auc_test']):>10}")

    lr = fit_logistic(rows)
    results["fitted logistic regression"] = lr
    print(f"  {'fitted logistic regression':<34}{lr['threshold']:>8.3f}"
          f"{lr['ba_val']:>9.4f}{lr['ba_test']:>9.4f}{fmt(lr['auc_test']):>10}")

    print("\n  fitted coefficients (log-odds of 'supported'):")
    for k, v in lr["coefficients"].items():
        print(f"    {k:<18}{v:>9.4f}")
    print(f"    {'intercept':<18}{lr['intercept']:>9.4f}")
    print("\n  A large positive coefficient means the mechanism pushes toward")
    print("  SUPPORTED; a large negative one pushes toward UNSUPPORTED. These")
    print("  are estimates from held-out data, not chosen values.")

    # ── 2. ablation ─────────────────────────────────────────────────────────
    banner("2. ABLATION   (cumulative, in pipeline order)")
    print(f"  {'configuration':<34}{'thresh':>8}{'BA test':>9}{'AUC test':>10}")
    print("  " + "-" * 62)
    prev = None
    for name, fn in ABLATION:
        res = evaluate(rows, fn)
        flag = ""
        if (prev is not None and abs(res["ba_test"] - prev[0]) < 1e-9
                and abs((res["auc_test"] or 0) - (prev[1] or 0)) < 1e-9):
            flag = "   <-- identical on BOTH metrics: not wired in?"
        print(f"  {name:<34}{res['threshold']:>8.3f}{res['ba_test']:>9.4f}"
              f"{fmt(res['auc_test']):>10}{flag}")
        prev = (res["ba_test"], res["auc_test"])

    # ── 3. per-type detection ───────────────────────────────────────────────
    banner("3. DETECTION BY PERTURBATION TYPE   (test split)")
    rules_to_show = ["entailment only", "0.3 sim + 0.7 entail (current)",
                     "fitted logistic regression"]
    tables = {n: per_type(results[n]) for n in rules_to_show}
    keys = sorted({k for t in tables.values() for k in t},
                  key=lambda k: (k == "SUPPORTED (controls)", k))
    print(f"  {'type':<26}" + "".join(f"{n[:16]:>18}" for n in rules_to_show)
          + f"{'95% CI (fitted)':>20}")
    print("  " + "-" * 82)
    for k in keys:
        cells = "".join(
            f"{str(tables[r][k][0]) + '/' + str(tables[r][k][1]):>18}" if k in tables[r]
            else f"{'-':>18}" for r in rules_to_show)
        best = tables["fitted logistic regression"].get(k)
        ci = ""
        if best:
            lo, hi = wilson(best[0], best[1])
            ci = f"[{lo*100:.0f}, {hi*100:.0f}]"
            if best[1] < 20:
                ci += " *"
        print(f"  {k:<26}{cells}{ci:>20}")
    print("\n  Cells are counts (correct / total), not rates — at these sample")
    print("  sizes a percentage implies precision the data cannot support.")
    print("  For negatives 'correct' means rejected; for controls, kept.")
    print("  * marks cells under n=20: indicative only, not a basis for")
    print("    comparing mechanisms. The reliable figure is AUC on the full")
    print("    test split.")

    # ── 4. condition_dropped, split by marker ───────────────────────────────
    banner("4. CONDITION_DROPPED, SPLIT BY NEGATION MARKER IN THE CLAIM")
    import re
    NEG = re.compile(r"\b(not|never|no|cannot|can't|prohibited|forbidden|"
                     r"disallowed|except|unless|avoid)\b", re.I)
    res = results["0.3 sim + 0.7 entail (current)"]
    buckets = defaultdict(lambda: [0, 0])
    for r, p in zip(res["test_rows"], res["test_pred"]):
        if r["perturbation_type"] != "condition_dropped":
            continue
        key = "claim HAS a marker" if NEG.search(r["claim"]) else "claim is marker-free"
        buckets[key][1] += 1
        buckets[key][0] += 1 if p == 0 else 0
    if buckets:
        for k, (hit, n) in buckets.items():
            print(f"  {k:<26}{hit}/{n}  ({hit/n*100:.1f}% detected)")
        print("\n  Marker-free claims route to the 0.8 branch of _negation_check —")
        print("  the branch the 2026-09-25 fix made reachable. Claims carrying a")
        print("  marker of their own route to the 1.0 branch, where the negation")
        print("  mechanism cannot contribute at all. A gap between these two rows")
        print("  is a measured limitation of presence-based negation detection.")
    else:
        print("  (no condition_dropped rows in the test split)")

    # ── optional CSV ────────────────────────────────────────────────────────
    if args.csv:
        with args.csv.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["table", "row", "metric", "value"])
            for name, res in results.items():
                w.writerow(["combination", name, "threshold", res["threshold"]])
                w.writerow(["combination", name, "ba_test", res["ba_test"]])
                w.writerow(["combination", name, "auc_test", res["auc_test"]])
            for rule, table in tables.items():
                for k, (hit, n, rate) in table.items():
                    w.writerow([f"per_type::{rule}", k, "detection_rate", rate])
                    w.writerow([f"per_type::{rule}", k, "n", n])
        print(f"\nTables written to {args.csv}")

    print()


if __name__ == "__main__":
    main()
