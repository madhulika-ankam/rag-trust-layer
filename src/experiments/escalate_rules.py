"""Compare ESCALATE rules on the 30 human-labelled answers.

A false ESCALATE on an answer the author read and judged sound is the most
expensive error this layer can make: it tells an operator the manual
contradicts itself when it does not.
"""
import csv, json, re, sys
sys.path.insert(0, '.')
from src.trust_layer.scorer import _aggregate
from src.trust_layer.decision import ANSWER_THRESHOLD, WARN_THRESHOLD
from src.trust_layer.verifier import SUPPORTED_SCORE, CONTRADICTION_THRESH

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

def live(ch):  return [c for c in ch if not c['gated']]

def verdict(ch, rule):
    """Return (verdict, score) for one claim under one ESCALATE rule."""
    ok = live(ch)
    if not ok: return 'UNSUPPORTED', 0.0
    best = max(ok, key=lambda c: c['comb'])
    supported = best['comb'] >= SUPPORTED_SCORE

    if rule == 'winning-chunk':
        contr = best['c']
    elif rule == 'support-first':                       # current
        contr = max(c['c'] for c in ok)
    elif rule == 'top-similarity':
        # only the chunk the retriever ranked most relevant may contradict
        contr = max(ok, key=lambda c: c['sim'])['c']
    elif rule == 'two-chunks':
        above = sorted((c['c'] for c in ok), reverse=True)
        contr = above[1] if len(above) > 1 else 0.0
    elif rule == 'high-bar-0.9':
        contr = max(c['c'] for c in ok)
        if contr <= 0.90: contr = 0.0
    elif rule == 'none':
        contr = 0.0
    else:
        raise ValueError(rule)

    if supported:  return 'SUPPORTED', best['comb']
    if contr > CONTRADICTION_THRESH: return 'CONTRADICTION', best['comb']
    return 'UNSUPPORTED', best['comb']

def decide(claims, rule, agg='current'):
    if not claims: return 'REFUSE'
    vs, sc = [], []
    for cl in claims:
        v, s = verdict(cl['chunks'], rule)
        vs.append(v); sc.append(s)
    if 'CONTRADICTION' in vs: return 'ESCALATE'
    t = _aggregate(sc, vs, agg)
    return 'ANSWER' if t >= ANSWER_THRESHOLD else ('WARN' if t >= WARN_THRESHOLD else 'REFUSE')

RULES = ['winning-chunk', 'top-similarity', 'two-chunks', 'high-bar-0.9',
         'support-first', 'none']
groups = ('fully good', 'incomplete', 'off-target', 'partly grounded')
rows = [(q, bucket(r)) for q, r in lab.items() if q in per]

print(f"  n={len(rows)} labelled answers   "
      + "  ".join(f"{g} {sum(1 for _, b in rows if b == g)}" for g in groups))
print(f"\n  {'rule':<16}{'false ESCALATE':>16}{'delivered':>12}{'withheld':>12}{'delivered':>12}")
print(f"  {'':<16}{'on FULLY GOOD':>16}{'fully good':>12}{'FABRICATN':>12}{'off-target':>12}")
print('  ' + '-' * 70)
for rule in RULES:
    d = {q: decide(per[q]['claims'], rule) for q, _ in rows}
    fe = sum(1 for q, b in rows if b == 'fully good' and d[q] == 'ESCALATE')
    dg = sum(1 for q, b in rows if b == 'fully good' and d[q] in ('ANSWER', 'WARN'))
    wf = sum(1 for q, b in rows if b == 'partly grounded' and d[q] not in ('ANSWER', 'WARN'))
    do = sum(1 for q, b in rows if b == 'off-target' and d[q] in ('ANSWER', 'WARN'))
    ng = sum(1 for _, b in rows if b == 'fully good')
    nf = sum(1 for _, b in rows if b == 'partly grounded')
    no = sum(1 for _, b in rows if b == 'off-target')
    print(f"  {rule:<16}{f'{fe}/{ng}':>16}{f'{dg}/{ng}':>12}{f'{wf}/{nf}':>12}{f'{do}/{no}':>12}")

print("\n  total CONTRADICTION claims over all 161 answers")
for rule in RULES:
    n = sum(1 for r in per.values() for cl in r['claims']
            if verdict(cl['chunks'], rule)[0] == 'CONTRADICTION')
    tot = sum(len(r['claims']) for r in per.values())
    print(f"    {rule:<16}{n:>5} / {tot}")

print("\n  ESCALATE by group, per rule")
print(f"  {'rule':<16}" + "".join(f"{g:>14}" for g in groups))
print('  ' + '-' * 72)
for rule in RULES:
    d = {q: decide(per[q]['claims'], rule) for q, _ in rows}
    line = f"  {rule:<16}"
    for g in groups:
        gq = [q for q, b in rows if b == g]
        line += f"{sum(1 for q in gq if d[q] == 'ESCALATE')}/{len(gq):<12}".rjust(14)
    print(line)

print("\n  every claim 'top-similarity' calls a CONTRADICTION, over all 161")
for q, r in sorted(per.items()):
    for cl in r['claims']:
        v, _ = verdict(cl['chunks'], 'top-similarity')
        if v == 'CONTRADICTION':
            ok = live(cl['chunks']); top = max(ok, key=lambda c: c['sim'])
            b = bucket(lab[q]) if q in lab else '-'
            print(f"    q{q:<4} {b:<16} c={top['c']:.2f} sim={top['sim']:.2f}  {cl['claim'][:78]}")
