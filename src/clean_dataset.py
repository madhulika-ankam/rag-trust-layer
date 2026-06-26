import pandas as pd

INPUT = "data/processed/multi_pdf_eval_deduplicated.xls"
OUTPUT = "data/processed/qa_pairs_clean.csv"

# Mac Roman misread of UTF-8 smart punctuation -> plain ASCII equivalents
REPLACEMENTS = {
    "‚Äú": '"',   # ‚Äú  -> left double quote
    "‚Äù": '"',   # ‚Äù  -> right double quote
    "‚Äô": "'",   # ‚Äô  -> apostrophe
    "‚Äì": "-",   # ‚Äì  -> en dash
    "‚Äî": "-",   # ‚Äî  -> em dash
}


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return text
    for bad, good in REPLACEMENTS.items():
        text = text.replace(bad, good)
    return text


def main():
    df = pd.read_excel(INPUT)
    print(f"Loaded {len(df)} rows from {INPUT}")

    df["question"] = df["question"].apply(clean_text)
    df["gold_answer"] = df["gold_answer"].apply(clean_text)

    # Add empty column for expected_decision labels (to be filled manually)
    df["expected_decision"] = ""

    df.to_csv(OUTPUT, index=False)
    print(f"Saved cleaned dataset to {OUTPUT}")

    # Spot-check the previously affected rows
    sample = df[df["gold_answer"].str.contains('"') | df["gold_answer"].str.contains("'")]
    print(f"\nSample of cleaned rows ({len(sample)} contain quotes now):")
    for _, row in sample.head(3).iterrows():
        print(f"  Q: {row['question'][:80]}")
        print(f"  A: {row['gold_answer'][:120]}")
        print()


if __name__ == "__main__":
    main()
