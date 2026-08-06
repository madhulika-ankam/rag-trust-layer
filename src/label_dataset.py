"""
Auto-label expected_decision for each Q&A pair using keyword heuristics.

Decision criteria:
  ESCALATE — answer contains safety-critical prohibitions, harm language, or
             specific safety thresholds (temperatures, codes, chemical %).
             A hallucinated answer here could directly cause injury.
  WARN     — answer is partial, hedged, or only partially grounded in the KB.
  REFUSE   — question cannot be adequately answered from the KB.
  ANSWER   — clear, complete, factual/procedural answer fully supported by KB.

Precedence: ESCALATE > WARN > ANSWER (REFUSE requires manual review).
"""
import re
import pandas as pd

INPUT = "data/processed/qa_pairs_clean.csv"
OUTPUT = "data/processed/qa_pairs_labeled.csv"
REVIEW_OUTPUT = "data/processed/label_review.csv"

# --- Keyword lists --------------------------------------------------------

ESCALATE_PHRASES = [
    # explicit prohibitions
    r"\bdo not\b", r"\bnever\b", r"\bmust not\b", r"\bdo not\b",
    r"\bnot allowed\b", r"\bnot permitted\b", r"\bprohibited\b",
    r"\bcannot\b", r"\bshould not\b",
    # harm / danger language
    r"\bwarning\b", r"\bdanger\b", r"\bhazard\b", r"\bcaution\b",
    r"\binjury\b", r"\binjuries\b", r"\bfatal\b", r"\bdeath\b",
    r"\bsevere\b", r"\bserious\b", r"\bdamage\b", r"\belectric shock\b",
    r"\belectrocution\b", r"\bamputation\b", r"\bburn\b",
    r"\blockout\b", r"\btagout\b", r"\benergy control\b",
    # safety equipment requirements
    r"\bppe\b", r"\bpersonal protective equipment\b", r"\bguard\b",
    r"\bsafety glasses\b", r"\bface shield\b",
    # specific safety-critical thresholds or codes
    r"\bosha\b", r"\bniosh\b", r"\b29 cfr\b", r"\b1910\.\d+\b",
]

WARN_PHRASES = [
    r"\btypically\b", r"\bgenerally\b", r"\bsuggests?\b",
    r"\bshould consider\b", r"\bcan vary\b", r"\bin some cases\b",
    r"\bdepending on\b", r"\bif applicable\b",
    r"\bmay be required\b", r"\bmight be required\b",
    r"\bmay be needed\b", r"\bmight be needed\b",
]

# -------------------------------------------------------------------------


def classify(question: str, answer: str) -> tuple[str, str]:
    """Return (decision, reason) for a Q&A pair."""
    answer_lower = answer.lower()
    question_lower = question.lower()

    # Check ESCALATE first (highest priority)
    for pattern in ESCALATE_PHRASES:
        if re.search(pattern, answer_lower):
            matched = re.search(pattern, answer_lower).group()
            return "ESCALATE", f"safety keyword: '{matched}'"

    # ESCALATE on numbers that look like safety thresholds or percentages
    if re.search(r"\d+\s*%", answer_lower):
        return "ESCALATE", "contains percentage threshold"
    if re.search(r"\d+\s*(°|degrees|rpm|lbs?|kg|psi|bar|volts?|amps?|db)", answer_lower, re.IGNORECASE):
        return "ESCALATE", "contains physical safety threshold"

    # Check WARN
    for pattern in WARN_PHRASES:
        if re.search(pattern, answer_lower):
            matched = re.search(pattern, answer_lower).group()
            return "WARN", f"hedging language: '{matched}'"

    return "ANSWER", "complete procedural/factual answer"


def main():
    df = pd.read_csv(INPUT)
    print(f"Loaded {len(df)} rows")

    labels, reasons = [], []
    for _, row in df.iterrows():
        decision, reason = classify(str(row["question"]), str(row["gold_answer"]))
        labels.append(decision)
        reasons.append(reason)

    df["expected_decision"] = labels
    df["label_reason"] = reasons

    # Save full labeled dataset
    df.to_csv(OUTPUT, index=False)
    print(f"Saved labeled dataset to {OUTPUT}")

    # Save borderline/review candidates (WARN rows + very short ESCALATE)
    review = df[df["expected_decision"].isin(["WARN", "REFUSE"])].copy()
    review.to_csv(REVIEW_OUTPUT, index=False)
    print(f"Saved {len(review)} rows for manual review to {REVIEW_OUTPUT}")

    # Summary
    counts = df["expected_decision"].value_counts()
    print("\n=== Label Distribution ===")
    for label, count in counts.items():
        pct = 100 * count / len(df)
        print(f"  {label:8s}: {count:3d}  ({pct:.1f}%)")

    print("\n=== Sample ESCALATE rows ===")
    for _, row in df[df["expected_decision"] == "ESCALATE"].head(5).iterrows():
        print(f"  Q: {row['question'][:80]}")
        print(f"  A: {row['gold_answer'][:120]}")
        print(f"  Reason: {row['label_reason']}")
        print()

    print("=== Sample WARN rows ===")
    for _, row in df[df["expected_decision"] == "WARN"].head(5).iterrows():
        print(f"  Q: {row['question'][:80]}")
        print(f"  A: {row['gold_answer'][:120]}")
        print(f"  Reason: {row['label_reason']}")
        print()


if __name__ == "__main__":
    main()
