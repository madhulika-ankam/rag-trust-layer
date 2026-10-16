import csv, json, re, sys
sys.path.insert(0, '.')
from collections import Counter
from src.trust_layer.scorer import _aggregate, AGGREGATOR
from src.trust_layer.decision import ANSWER_THRESHOLD, WARN_THRESHOLD

lab = {r['question_id']: r for r in
       csv.DictReader(open('data/processed/answer_review_done.csv', encoding='utf-8-sig'))
       if (r.get('grounded') or '').strip()}
key = {r['question_id']: r for r in
       csv.DictReader(open('data/processed/answer_review_key.csv', encoding='utf-8'))}
VER = sys.argv[1] if len(sys.argv) > 1 else 'data/processed/verified.jsonl'
recs = {str(json.loads(l)['question_id']): json.loads(l)
        for l in open(VER, encoding='utf-8')}

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

def now(c):
    if not c: return 'REFUSE'
    if any(x['verdict'] == 'CONTRADICTION' for x in c): return 'ESCALATE'
    s = _aggregate([x['combined'] for x in c], [x['verdict'] for x in c], AGGREGATOR)
    return 'ANSWER' if s >= ANSWER_THRESHOLD else ('WARN' if s >= WARN_THRESHOLD else 'REFUSE')

D = lambda d: 'deliver ' if d in ('ANSWER', 'WARN') else 'WITHHOLD'
rows = []
for qid, r in lab.items():
    if qid not in recs: continue
    rows.append((qid, bucket(r), key[qid]['decision_current'], now(recs[qid]['claims'])))
rows.sort(key=lambda x: (x[1], int(x[0])))

print("  every one of your 30, THEN (when you labelled) vs NOW (after the fixes)\n")
print(f"  {'qid':>4}  {'YOUR JUDGEMENT':<16} {'THEN':<9}{'':<10}{'NOW':<9}{'':<10}{'changed?'}")
print('  ' + '-' * 72)
last = None
for qid, b, then, n in rows:
    if b != last:
        print(); last = b
    mark = '' if then == n else '   <-- changed'
    print(f"  {qid:>4}  {b:<16} {then:<9}{D(then):<10}{n:<9}{D(n):<10}{mark}")

print("\n  " + "=" * 70)
print("  SUMMARY — how many of each group get DELIVERED\n")
print(f"  {'your judgement':<17}{'THEN':>12}{'NOW':>12}")
print('  ' + '-' * 40)
for b in ('fully good', 'incomplete', 'off-target', 'partly grounded'):
    g = [r for r in rows if r[1] == b]
    t = sum(1 for _, _, th, _ in g if th in ('ANSWER', 'WARN'))
    n = sum(1 for _, _, _, nn in g if nn in ('ANSWER', 'WARN'))
    print(f"  {b:<17}{f'{t}/{len(g)}':>12}{f'{n}/{len(g)}':>12}")

print()
print("  ESCALATE (false alarms) by group")
print('  ' + '-' * 40)
for b in ('fully good', 'incomplete', 'off-target', 'partly grounded'):
    g = [r for r in rows if r[1] == b]
    t = sum(1 for _, _, th, _ in g if th == 'ESCALATE')
    n = sum(1 for _, _, _, nn in g if nn == 'ESCALATE')
    print(f"  {b:<17}{f'{t}/{len(g)}':>12}{f'{n}/{len(g)}':>12}")
