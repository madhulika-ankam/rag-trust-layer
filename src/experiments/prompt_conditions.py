#!/usr/bin/env python3
"""
prompt_conditions.py — does the trust layer earn its keep when the generator
is NOT already guarded?

THE PROBLEM THIS ANSWERS
    The headline result ("the layer withholds 7 of 13 sound answers and
    catches almost nothing") is a result about ONE generator configuration:
    the `guarded` prompt, which already instructs the model to abstain when
    the context is insufficient. Of 30 answers read by hand, exactly one
    contained content the manuals do not support. There was almost nothing
    for the layer to catch.

    That is a statement about the prompt, not about the layer. Four prompt
    conditions were generated over the same 161 questions with the same
    retrieval, so the layer's value can be measured as a function of how
    safe the generator already is.

CONDITIONS (all frozen in data/processed/generations_*.jsonl)
    minimal   context + question, no instruction at all
    grounded  + "use ONLY the context"
    guarded   + "if the context is insufficient, say so"   <- the default
    stress    guarded prompt, degraded retrieval (differs on 62/161 questions)

WHAT IS AND IS NOT GROUND TRUTH
    The author's 30 hand labels were made on the GUARDED answers. The other
    conditions produced different text for the same questions, so those
    labels DO NOT transfER. Two things are therefore reported separately:

      1. layer behaviour across conditions on the same 30 questions
         — valid, no labels needed
      2. the ESCALATE-labelled subset: questions whose gold answer indicates
         the manuals do not contain an answer. A substantive answer to one
         of these is unsupported by construction. This is a PROXY, and the
         labels behind it are regex-generated (see facts.md section 2).

USAGE
    venv/bin/python src/experiments/prompt_conditions.py
"""
from __future__ import annotations

import csv
import json
import re
import statistics as st
import sys

sys.path.insert(0, ".")
from src.trust_layer.decision import ANSWER_THRESHOLD, WARN_THRESHOLD
from src.trust_layer.scorer import AGGREGATOR, _aggregate

CONDITIONS = {
    "minimal": "data/processed/verified_minimal.jsonl",
    "grounded": "data/processed/verified_grounded.jsonl",
    "guarded": "data/processed/verified.jsonl",
    "stress": "data/processed/verified_stress.jsonl",
}


def decide(rec: dict) -> str:
    claims = rec["claims"]
    if rec.get("declined_to_answer"):
        return "DECLINED"
    if not claims:
        return "REFUSE"
    verdicts = [c["verdict"] for c in claims]
    if "CONTRADICTION" in verdicts:
        return "ESCALATE"
    s = _aggregate([c["combined"] for c in claims], verdicts, AGGREGATOR)
    return "ANSWER" if s >= ANSWER_THRESHOLD else ("WARN" if s >= WARN_THRESHOLD else "REFUSE")


def bucket(r: dict) -> str:
    l = (r["grounded"] or "").strip().lower()
    n = (r["notes"] or "").lower()
    if "partly" in l:
        return "partly grounded"
    if "off" in l and "target" in l:
        return "off-target"
    if "incomplete" in l or re.search(
            r"incomplete|not complete|doesn.?t answer|didnt answer|missed|abruptly", n):
        return "incomplete"
    return "fully good"


def main() -> None:
    data = {}
    for name, path in CONDITIONS.items():
        data[name] = {r["question_id"]: r
                      for r in (json.loads(l) for l in open(path, encoding="utf-8"))}

    labels = {int(r["question_id"]): r for r in csv.DictReader(
        open("data/processed/answer_review_done.csv", encoding="utf-8-sig"))
        if (r.get("grounded") or "").strip()}
    thirty = sorted(labels)
    groups = {q: bucket(labels[q]) for q in thirty}

    print(f"  aggregator {AGGREGATOR}   ANSWER>={ANSWER_THRESHOLD}  "
          f"WARN>={WARN_THRESHOLD}\n")

    # ---- 1. all 161: what the generator does, and what the layer does -----
    print("  1. ALL 161 QUESTIONS — generator behaviour and layer decisions\n")
    print(f"  {'condition':<10}{'declined':>9}{'claims':>8}{'mean ent':>10}"
          f"{'SUPP':>7}{'CONTR':>7}   {'ANSWER':>7}{'WARN':>6}{'REFUSE':>8}{'ESCAL':>7}")
    print("  " + "-" * 88)
    for name in CONDITIONS:
        recs = list(data[name].values())
        claims = [c for r in recs for c in r["claims"]]
        dec = [decide(r) for r in recs]
        print(f"  {name:<10}{sum(1 for r in recs if r['declined_to_answer']):>9}"
              f"{len(claims):>8}"
              f"{st.mean(c['entailment_p'] for c in claims):>10.3f}"
              f"{sum(1 for c in claims if c['verdict'] == 'SUPPORTED') / len(claims) * 100:>6.0f}%"
              f"{sum(1 for c in claims if c['verdict'] == 'CONTRADICTION'):>7}"
              f"   {dec.count('ANSWER'):>7}{dec.count('WARN'):>6}"
              f"{dec.count('REFUSE') + dec.count('DECLINED'):>8}{dec.count('ESCALATE'):>7}")

    # ---- 2. the ESCALATE subset — induced hallucination, by proxy --------
    esc = [q for q, r in data["guarded"].items() if r["expected_decision"] == "ESCALATE"]
    print(f"\n  2. THE {len(esc)} QUESTIONS LABELLED ESCALATE "
          "(gold answer indicates the manuals do not answer them)")
    print("     A substantive answer here is unsupported BY CONSTRUCTION.")
    print("     Withheld = REFUSE, ESCALATE or the generator declining.\n")
    print(f"  {'condition':<10}{'generator answered':>20}{'layer withheld':>17}"
          f"{'delivered anyway':>19}")
    print("  " + "-" * 68)
    for name in CONDITIONS:
        answered = sum(1 for q in esc if not data[name][q]["declined_to_answer"])
        dec = {q: decide(data[name][q]) for q in esc}
        withheld = sum(1 for q in esc if dec[q] not in ("ANSWER", "WARN"))
        print(f"  {name:<10}{f'{answered}/{len(esc)}':>20}"
              f"{f'{withheld}/{len(esc)}':>17}"
              f"{len(esc) - withheld:>19}")

    # ---- 3. the 30 hand-labelled questions, across conditions ------------
    print(f"\n  3. THE {len(thirty)} HAND-LABELLED QUESTIONS, same questions,"
          " four conditions")
    print("     Labels were made on GUARDED answers and do not transfer to the")
    print("     other columns. Read this as layer BEHAVIOUR, not accuracy.\n")
    print(f"  {'her judgement':<17}{'n':>3}" +
          "".join(f"{c:>11}" for c in CONDITIONS))
    print("  " + "-" * 66)
    for g in ("fully good", "incomplete", "off-target", "partly grounded"):
        qs = [q for q in thirty if groups[q] == g]
        row = f"  {g:<17}{len(qs):>3}"
        for name in CONDITIONS:
            d = sum(1 for q in qs if decide(data[name][q]) in ("ANSWER", "WARN"))
            row += f"{f'{d} deliv':>11}"
        print(row)

    print("\n     generator declined, within these 30")
    row = f"  {'':<20}"
    for name in CONDITIONS:
        row += f"{sum(1 for q in thirty if data[name][q]['declined_to_answer']):>11}"
    print(row)


if __name__ == "__main__":
    main()


def addendum() -> None:
    """Config A (no trust layer) vs Config D (trust layer), per condition.

    Without the layer every generated answer reaches the user, so Config A is
    simply "did the generator produce an answer". The comparison is split by
    the question's expected_decision because the two sides trade off:

      on ESCALATE questions  withholding is CORRECT   -> benefit
      on ANSWER questions    withholding is a COST    -> over-abstention
    """
    import csv, json, sys
    data = {name: {r["question_id"]: r for r in
                   (json.loads(l) for l in open(path, encoding="utf-8"))}
            for name, path in CONDITIONS.items()}
    guarded = data["guarded"]
    esc = [q for q, r in guarded.items() if r["expected_decision"] == "ESCALATE"]
    ans = [q for q, r in guarded.items() if r["expected_decision"] == "ANSWER"]

    print("\n\n  4. CONFIG A (no layer) vs CONFIG D (layer)")
    print("     Without the layer, every generated answer is delivered.\n")
    print(f"  {'':<10}{'UNSUPPORTED delivered':>24}{'':<4}"
          f"{'ANSWERABLE delivered':>22}")
    print(f"  {'condition':<10}{'no layer':>11}{'layer':>13}{'':<4}"
          f"{'no layer':>11}{'layer':>11}")
    print("  " + "-" * 64)
    for name in CONDITIONS:
        d = data[name]
        a_bad = sum(1 for q in esc if not d[q]["declined_to_answer"])
        l_bad = sum(1 for q in esc if decide(d[q]) in ("ANSWER", "WARN"))
        a_ok = sum(1 for q in ans if not d[q]["declined_to_answer"])
        l_ok = sum(1 for q in ans if decide(d[q]) in ("ANSWER", "WARN"))
        print(f"  {name:<10}{f'{a_bad}/{len(esc)}':>11}{f'{l_bad}/{len(esc)}':>13}"
              f"{'':<4}{f'{a_ok}/{len(ans)}':>11}{f'{l_ok}/{len(ans)}':>11}")

    print("\n     Read the left block as the benefit and the right as the cost.")
    print("     ⚠ expected_decision is REGEX-GENERATED and unvalidated. It")
    print("       disagrees with the author's own reading on q23 and q139.")
    print("       This is a proxy for groundedness, not a measurement of it.")


if __name__ == "__main__":
    addendum()
