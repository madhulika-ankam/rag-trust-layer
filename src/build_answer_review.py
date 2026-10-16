#!/usr/bin/env python3
"""
build_answer_review.py — worksheet for hand-labelling answer groundedness.

WHY THIS EXISTS
    Two numbers in EVALUATION_PLAN.md cannot be computed without a human
    reading answers beside their evidence:

      unsupported-answer delivery rate   the headline metric (Group 2)
      the risk axis of the risk-coverage curve  (Group 3)

    The trust layer's own verdicts cannot supply them. Using them would be
    grading your own homework — the layer decides what to deliver AND scores
    how grounded the delivered answers were. Ground truth has to come from
    outside the thing being measured.

WHAT IT SAMPLES
    TOP     every answer scoring >= 0.2. These are what gets delivered at any
            threshold you would realistically use, so they carry the risk
            axis. Small enough to label exhaustively.

    BOTTOM  a seeded random sample of the low-scoring pile. These were
            refused; the question is whether the refusals were RIGHT.
            Both a correct refusal and a wrong one score low, so only
            reading distinguishes them:

              answer really is fabricated  -> correct refusal, the
                                              generator is the constraint
              answer is actually fine      -> wrong refusal, the verifier is

            That is the Break #1 vs Break #3 question, measured instead of
            guessed. A sample suffices because this estimates a proportion.

    Answers that declined to answer are skipped: no claims, nothing to judge.

USAGE
    python -m src.build_answer_review
    python -m src.build_answer_review --bottom 40
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path

# The worksheet is BLINDED. system_score, system_decision and
# expected_decision are deliberately withheld: seeing that the system scored
# an answer 0.19 and refused it would anchor the judgement, and these labels
# exist precisely to be independent of the system being measured. They are
# written to a separate key file and rejoined by question_id for analysis.
FIELDS = [
    "question_id", "question", "generated_answer", "gold_answer",
    "retrieved_evidence", "grounded", "notes",
]
KEY_FIELDS = ["question_id", "pile", "system_score", "system_decision",
              "expected_decision"]

# Four labels, mapping one-to-one onto the four decisions the trust layer
# can make. The ungrounded/contradicted split is the one that matters:
# absence of support is not the same as evidence against, and only the
# second should raise an alarm.
#
#   grounded     -> ANSWER      deliver it
#   partly       -> WARN        deliver with a caveat
#   ungrounded   -> REFUSE      withhold; evidence is silent
#   contradicted -> ESCALATE    withhold and flag; evidence says otherwise
GUIDANCE = (
    "grounded = every claim backed by the evidence | "
    "partly = some backed, some not | "
    "ungrounded = claims the evidence does not mention | "
    "contradicted = the evidence states otherwise"
)


def agg_min(claims):
    return min((c["combined"] for c in claims), default=0.0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verified", type=Path,
                    default=Path("data/processed/verified.jsonl"))
    ap.add_argument("--gen", type=Path,
                    default=Path("data/processed/generations.jsonl"))
    ap.add_argument("--out", type=Path,
                    default=Path("data/processed/answer_review.csv"))
    ap.add_argument("--cut", type=float, default=0.2,
                    help="score boundary between the two piles")
    ap.add_argument("--bottom", type=int, default=30,
                    help="how many low-scoring answers to sample")
    ap.add_argument("--seed", type=int, default=20261001)
    args = ap.parse_args()

    verified = [json.loads(l) for l in args.verified.open(encoding="utf-8")]
    chunks_by_q = {json.loads(l)["question_id"]: json.loads(l)["retrieved_chunks"]
                   for l in args.gen.open(encoding="utf-8")}

    scored = [(agg_min(r["claims"]), r) for r in verified if r["claims"]]
    top = [r for s, r in scored if s >= args.cut]
    bottom = [r for s, r in scored if s < args.cut]

    rng = random.Random(args.seed)
    sample = rng.sample(bottom, min(args.bottom, len(bottom)))

    rows, keys = [], []
    for pile, group in (("TOP (delivered)", top), ("BOTTOM (refused)", sample)):
        for r in group:
            evidence = "\n\n".join(
                f"[{c['source_file']} p.{c['page']}]\n" + " ".join(c["content"].split())
                for c in chunks_by_q.get(r["question_id"], [])
            )
            keys.append({
                "question_id": r["question_id"],
                "pile": pile,
                "system_score": round(agg_min(r["claims"]), 4),
                "system_decision": ("ESCALATE" if any(
                    c["verdict"] == "CONTRADICTION" for c in r["claims"]) else "REFUSE/other"),
                "expected_decision": r["expected_decision"],
            })
            rows.append({
                "question_id": r["question_id"],
                "question": r["question"],
                "generated_answer": r["generated_answer"],
                "gold_answer": r["gold_answer"],
                "retrieved_evidence": evidence,
                "label_options": GUIDANCE,
                "grounded": "",
                "notes": "",
            })

    # Shuffled, so the order itself carries no signal about which pile a
    # row came from or how the system scored it.
    rng.shuffle(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    key_path = args.out.with_name(args.out.stem + "_key.csv")
    with key_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=KEY_FIELDS); w.writeheader(); w.writerows(keys)

    print(f"Wrote {len(rows)} rows to {args.out}")
    print(f"Hidden key (do not open while labelling): {key_path}\n")
    print(f"  TOP    (score >= {args.cut})   {len(top):>4}   label ALL of these")
    print(f"  BOTTOM (score <  {args.cut})   {len(sample):>4}   sampled from {len(bottom)}")
    print(f"  skipped (declined / no claims) {sum(1 for r in verified if not r['claims']):>4}")
    print(f"\nFill the 'grounded' column with one of:")
    print("  grounded / partly / ungrounded")
    print(f"\n  {GUIDANCE}")
    print("\nJudge the ANSWER against the EVIDENCE column only.")
    print("gold_answer is there for context — do NOT mark an answer ungrounded")
    print("merely because it differs from the gold answer. The question is")
    print("whether the retrieved evidence supports what was said.")


if __name__ == "__main__":
    main()
