import json, statistics as st
from collections import defaultdict

import sys
VER = sys.argv[1] if len(sys.argv) > 1 else 'data/processed/verified.jsonl'
recs = [json.loads(l) for l in open(VER, encoding='utf-8')]
claims = [c for r in recs for c in r['claims']]
for c in claims:
    c['_w'] = len(c['claim'].split())

BANDS = [(0,8),(8,12),(12,16),(16,20),(20,26),(26,999)]
print(f"ENTAILMENT vs CLAIM (HYPOTHESIS) LENGTH — {len(claims)} claims, "
      f"sentence-level NLI\n{VER}\n")
print(f"  {'claim words':<14}{'n':>5}{'mean entail':>13}{'median':>9}{'% SUPPORTED':>14}{'mean sim':>10}")
print('  ' + '-' * 66)
for lo, hi in BANDS:
    g = [c for c in claims if lo <= c['_w'] < hi]
    if len(g) < 5: continue
    sup = sum(1 for c in g if c['verdict'] == 'SUPPORTED') / len(g) * 100
    print(f"  {f'{lo}-{hi if hi<999 else chr(43)}':<14}{len(g):>5}"
          f"{st.mean(c['entailment_p'] for c in g):>13.3f}"
          f"{st.median(c['entailment_p'] for c in g):>9.3f}{sup:>13.0f}%"
          f"{st.mean(c['similarity'] for c in g):>10.3f}")

short = [c for c in claims if c['_w'] < 12]
long_ = [c for c in claims if c['_w'] >= 20]
print(f"\n  short (<12 words)  n={len(short):>3}  mean entailment {st.mean(c['entailment_p'] for c in short):.3f}"
      f"   {sum(1 for c in short if c['verdict']=='SUPPORTED')/len(short)*100:.0f}% supported")
print(f"  long  (>=20 words) n={len(long_):>3}  mean entailment {st.mean(c['entailment_p'] for c in long_):.3f}"
      f"   {sum(1 for c in long_ if c['verdict']=='SUPPORTED')/len(long_)*100:.0f}% supported")

# similarity is the control: if long claims were simply more off-topic, their
# similarity would be lower too.
print(f"\n  CONTROL — mean similarity   short {st.mean(c['similarity'] for c in short):.3f}"
      f"   long {st.mean(c['similarity'] for c in long_):.3f}")
print("  If similarity is flat while entailment collapses, length is acting on")
print("  the NLI model specifically, not on topical relevance.")

try:
    from scipy.stats import spearmanr
    rho, p = spearmanr([c['_w'] for c in claims], [c['entailment_p'] for c in claims])
    rho2, p2 = spearmanr([c['_w'] for c in claims], [c['similarity'] for c in claims])
    print(f"\n  Spearman, length vs entailment : rho {rho:+.3f}  p {p:.2e}")
    print(f"  Spearman, length vs similarity : rho {rho2:+.3f}  p {p2:.2e}")
except ImportError:
    print("\n  (scipy not installed — correlation skipped)")
