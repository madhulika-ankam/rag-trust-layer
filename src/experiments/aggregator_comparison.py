"""Compare answer-level aggregators on the 30 labelled answers, with the
ESCALATE rule fixed to the one Step 3 selected (top-similarity)."""
import csv, json, re, sys
sys.path.insert(0, '.')
from src.trust_layer.verifier import SUPPORTED_SCORE, CONTRADICTION_THRESH
from src.trust_layer.decision import ANSWER_THRESHOLD, WARN_THRESHOLD

S = 'data/processed'
per = {r['qid']: r for r in (json.loads(l) for l in open(f'{S}/perchunk_sentence.jsonl', encoding='utf-8'))}
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
    top  = max(ok, key=lambda c: c['sim'])
    if best['comb'] >= SUPPORTED_SCORE: return 'SUPPORTED', best['comb']
    if top['c'] > CONTRADICTION_THRESH: return 'CONTRADICTION', best['comb']
    return 'UNSUPPORTED', best['comb']

def agg(sc, vs, rule):
    n = len(sc)
    if n == 0: return 0.0
    if rule == 'current':    return (sum(sc)/n) * (1 - sum(1 for v in vs if v != 'SUPPORTED')/n)
    if rule == 'proportion': return sum(1 for v in vs if v == 'SUPPORTED')/n
    if rule == 'min':        return min(sc)
    if rule == 'mean':       return sum(sc)/n
    if rule == 'max':        return max(sc)
    raise ValueError(rule)

def decide(claims, rule):
    if not claims: return 'REFUSE'
    vs, sc = zip(*[claim_verdict(c['chunks']) for c in claims])
    if 'CONTRADICTION' in vs: return 'ESCALATE'
    t = agg(list(sc), list(vs), rule)
    return 'ANSWER' if t >= ANSWER_THRESHOLD else ('WARN' if t >= WARN_THRESHOLD else 'REFUSE')

groups = ('fully good', 'incomplete', 'off-target', 'partly grounded')
rows = [(q, bucket(r)) for q, r in lab.items() if q in per]
N = {g: sum(1 for _, b in rows if b == g) for g in groups}

print(f"  ESCALATE rule fixed to top-similarity.  ANSWER>={ANSWER_THRESHOLD}  WARN>={WARN_THRESHOLD}\n")
print(f"  {'aggregator':<13}{'DELIVERED good':>16}{'withheld partly':>17}"
      f"{'delivered off':>15}{'delivered incompl':>19}")
print('  ' + '-' * 78)
for rule in ('current', 'proportion', 'mean', 'min', 'max'):
    d = {q: decide(per[q]['claims'], rule) for q, _ in rows}
    out = []
    for g, want_deliver in (('fully good', 1), ('partly grounded', 0), ('off-target', 1), ('incomplete', 1)):
        k = sum(1 for q, b in rows if b == g and
                ((d[q] in ('ANSWER', 'WARN')) == bool(want_deliver)))
        out.append(f"{k}/{N[g]}")
    print(f"  {rule:<13}{out[0]:>16}{out[1]:>17}{out[2]:>15}{out[3]:>19}")

print("\n  the 13 FULLY GOOD, decision under each aggregator")
hdr = f"  {'qid':>4} {'claims':>7}  " + "".join(f"{r:<11}" for r in ('current','proportion','mean','min'))
print(hdr); print('  ' + '-' * 60)
for q, b in sorted(rows, key=lambda x: x[0]):
    if b != 'fully good': continue
    line = f"  {q:>4} {len(per[q]['claims']):>7}  "
    for rule in ('current', 'proportion', 'mean', 'min'):
        line += f"{decide(per[q]['claims'], rule):<11}"
    print(line)

print("\n\n  THRESHOLD SWEEP — deliver when score >= WARN.  Constraint from the")
print("  plan: fabrication withheld >= 3/4 AND off-target delivered <= 1/7.")
print(f"\n  {'aggregator':<12}{'WARN':>6}{'good':>8}{'partly':>8}{'off':>8}{'incompl':>9}  ok?")
print('  ' + '-' * 60)
best = []
for rule in ('current', 'proportion', 'mean', 'min'):
    for w in [x / 20 for x in range(1, 20)]:
        d = {}
        for q, _ in rows:
            cl = per[q]['claims']
            if not cl: d[q] = 'REFUSE'; continue
            vs, sc = zip(*[claim_verdict(c['chunks']) for c in cl])
            d[q] = 'ESCALATE' if 'CONTRADICTION' in vs else (
                'deliver' if agg(list(sc), list(vs), rule) >= w else 'REFUSE')
        dl = lambda g: sum(1 for q, b in rows if b == g and d[q] == 'deliver')
        g_, f_, o_, i_ = dl('fully good'), N['partly grounded'] - dl('partly grounded'), dl('off-target'), dl('incomplete')
        ok = f_ >= 3 and o_ <= 1
        if ok: best.append((g_, rule, w, f_, o_, i_))
for g_, rule, w, f_, o_, i_ in sorted(best, reverse=True)[:12]:
    print(f"  {rule:<12}{w:>6.2f}{f'{g_}/13':>8}{f'{f_}/4':>8}{f'{o_}/7':>8}{f'{i_}/6':>9}  yes")
