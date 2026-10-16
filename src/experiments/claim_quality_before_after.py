import json, statistics as st, sys

def load(p):
    cs=[c for r in (json.loads(l) for l in open(p,encoding='utf-8')) for c in r['claims']]
    for c in cs: c['_w']=len(c['claim'].split())
    return cs

def row(name, cs):
    ws=[c['_w'] for c in cs]; e=[c['entailment_p'] for c in cs]
    sup=sum(1 for c in cs if c['verdict']=='SUPPORTED')/len(cs)*100
    con=sum(1 for c in cs if c['verdict']=='CONTRADICTION')
    print(f"  {name:<10}{len(cs):>6}{st.median(ws):>8.0f}{st.mean(ws):>8.1f}"
          f"{sum(1 for w in ws if w<12)/len(ws)*100:>9.0f}%"
          f"{st.mean(e):>11.3f}{st.median(e):>9.3f}{sup:>9.0f}%{con:>7}")

BEFORE = sys.argv[1] if len(sys.argv) > 2 else 'data/processed/verified_step1.jsonl'
AFTER  = sys.argv[2] if len(sys.argv) > 2 else 'data/processed/verified.jsonl'
a=load(BEFORE); b=load(AFTER)
print(f"  {'':<10}{'claims':>6}{'med w':>8}{'mean w':>8}{'<12w':>10}{'mean ent':>11}{'med ent':>9}{'SUPP':>9}{'CONTR':>7}")
print('  '+'-'*70)
row('before', a); row('after', b)

print("\n  entailment by length band, AFTER")
for lo,hi in [(0,8),(8,12),(12,16),(16,20),(20,26),(26,999)]:
    g=[c for c in b if lo<=c['_w']<hi]
    if len(g)<5: continue
    print(f"    {lo:>3}-{hi if hi<999 else '+':<4} n={len(g):>4}  ent {st.mean(c['entailment_p'] for c in g):.3f}"
          f"   {sum(1 for c in g if c['verdict']=='SUPPORTED')/len(g)*100:>3.0f}% supported")
