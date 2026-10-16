"""Claim length distribution straight from the decomposer — no NLI, seconds not minutes."""
import json, statistics as st, sys
sys.path.insert(0, '.')
from src.trust_layer.decomposer import decompose

recs = [json.loads(l) for l in open('data/processed/generations.jsonl', encoding='utf-8')]
claims = []
for r in recs:
    for c in decompose(r['generated_answer']):
        claims.append((r['question_id'], c, len(c.split())))

ws = [w for _, _, w in claims]
BANDS = [(0,8),(8,12),(12,16),(16,20),(20,26),(26,999)]
print(f"total claims {len(claims)}   median {st.median(ws):.0f}w   mean {st.mean(ws):.1f}w")
print(f"under 12 words: {sum(1 for w in ws if w < 12)} ({sum(1 for w in ws if w<12)/len(ws)*100:.0f}%)")
print(f"20+ words     : {sum(1 for w in ws if w >= 20)} ({sum(1 for w in ws if w>=20)/len(ws)*100:.0f}%)")
print()
for lo, hi in BANDS:
    n = sum(1 for w in ws if lo <= w < hi)
    print(f"  {lo:>3}-{hi if hi<999 else '+':<4} {n:>4}  {'#' * (n//4)}")

if len(sys.argv) > 1 and sys.argv[1] == '--longest':
    for qid, c, w in sorted(claims, key=lambda t: -t[2])[:15]:
        print(f"\nq{qid} ({w}w) {c}")
