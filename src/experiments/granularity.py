"""Chunk vs sentence NLI granularity, decided on the 30 labelled answers.

The previous attempt could not settle this: claims were long enough that
the length effect swamped the comparison. Claims are now shorter, so the
comparison is re-run on identical frozen generations with everything else
held fixed — same claims, same chunks, same ESCALATE rule, same aggregator.
"""
import csv, json, re, sys
sys.path.insert(0, '.')
from src.trust_layer.verifier import SUPPORTED_SCORE, CONTRADICTION_THRESH
from src.trust_layer.decision import ANSWER_THRESHOLD, WARN_THRESHOLD
from src.trust_layer.scorer import AGGREGATOR

S = 'data/processed'
FILES = {'sentence': f'{S}/perchunk_sentence.jsonl', 'chunk': f'{S}/perchunk_chunk.jsonl'}
lab = {int(r['question_id']): r for r in
       csv.DictReader(open('data/processed/answer_review_done.csv', encoding='utf-8-sig'))
       if (r.get('grounded') or '').strip()}

def bucket(r):
    l = r['grounded'].strip().lower(); n = (r['notes'] or '').lower()
    # The author's label is "partly", not "fabrication". Reading the four:
    # q42 is an omission, q126 incompleteness, q112 has no note, and only
    # q48 is content the manuals do not support. Calling the group
    # FABRICATION overstated what the system is catching.
    if 'partly' in l: return 'partly grounded'
    if 'off' in l and 'target' in l: return 'off-target'
    if 'incomplete' in l or re.search(r'incomplete|not complete|doesn.?t answer|didnt answer|missed|abruptly', n):
        return 'incomplete'
    return 'fully good'

def claim_verdict(ch):
    ok = [c for c in ch if not c['gated']]
    if not ok: return 'UNSUPPORTED', 0.0
    best = max(ok, key=lambda c: c['comb'])
    top  = max(ok, key=lambda c: c['sim'])          # Step 3's ESCALATE rule
    if best['comb'] >= SUPPORTED_SCORE: return 'SUPPORTED', best['comb']
    if top['c'] > CONTRADICTION_THRESH: return 'CONTRADICTION', best['comb']
    return 'UNSUPPORTED', best['comb']

def decide(claims):
    if not claims: return 'REFUSE'
    vs, sc = zip(*[claim_verdict(c['chunks']) for c in claims])
    if 'CONTRADICTION' in vs: return 'ESCALATE'
    t = min(sc) if AGGREGATOR == 'min' else sum(sc) / len(sc)
    return 'ANSWER' if t >= ANSWER_THRESHOLD else ('WARN' if t >= WARN_THRESHOLD else 'REFUSE')

groups = ('fully good', 'incomplete', 'off-target', 'partly grounded')
print(f"  aggregator {AGGREGATOR}   deliver >= {WARN_THRESHOLD}   ESCALATE rule: top-similarity chunk\n")
print(f"  {'granularity':<12}{'good deliv':>12}{'false ESC':>11}{'partly held':>13}"
      f"{'off deliv':>11}{'SUPPORTED':>11}{'CONTRA':>8}")
print('  ' + '-' * 76)
rowsets = {}
for name, path in FILES.items():
    per = {r['qid']: r for r in (json.loads(l) for l in open(path, encoding='utf-8'))}
    rows = [(q, bucket(r)) for q, r in lab.items() if q in per]
    d = {q: decide(per[q]['claims']) for q, _ in rows}
    rowsets[name] = (per, rows, d)
    N = {g: sum(1 for _, b in rows if b == g) for g in groups}
    dl = lambda g: sum(1 for q, b in rows if b == g and d[q] in ('ANSWER', 'WARN'))
    fe = sum(1 for q, b in rows if b == 'fully good' and d[q] == 'ESCALATE')
    allv = [claim_verdict(c['chunks'])[0] for r in per.values() for c in r['claims']]
    good = f"{dl('fully good')}/{N['fully good']}"
    fabr = f"{N['partly grounded'] - dl('partly grounded')}/{N['partly grounded']}"
    off = f"{dl('off-target')}/{N['off-target']}"
    sup = f"{allv.count('SUPPORTED')}/{len(allv)}"
    print(f"  {name:<12}{good:>12}{f'{fe}/13':>11}{fabr:>13}{off:>11}"
          f"{sup:>11}{allv.count('CONTRADICTION'):>8}")

print("\n  where the two disagree, on the 30 labelled answers")
_, rows, ds = rowsets['sentence']; _, _, dc = rowsets['chunk']
any_diff = False
for q, b in sorted(rows):
    if ds[q] != dc[q]:
        any_diff = True
        print(f"    q{q:<4} {b:<16} sentence {ds[q]:<9} chunk {dc[q]}")
if not any_diff:
    print("    (none — the two granularities decide all 30 identically)")
