"""Per-CHUNK verifier features for every claim, so ESCALATE rules can be
compared without re-running NLI once per rule."""
import json, sys, time
sys.path.insert(0, '.')
import src.trust_layer.verifier as V
from src.trust_layer.decomposer import decompose
from src.run_verification import looks_like_a_decline

GRAN = sys.argv[2] if len(sys.argv) > 2 else 'sentence'
V.NLI_GRANULARITY = GRAN
OUT = sys.argv[1] if len(sys.argv) > 1 else f'data/processed/perchunk_{GRAN}.jsonl'
out = open(OUT, 'w', encoding='utf-8')
recs = [json.loads(l) for l in open('data/processed/generations.jsonl', encoding='utf-8')]
t0 = time.time()
for n, rec in enumerate(recs, 1):
    ans = rec['generated_answer']
    claims = [] if (looks_like_a_decline(ans) or not ans.strip()) else decompose(ans)
    rows = []
    for claim in claims:
        per = []
        for ch in rec['retrieved_chunks']:
            ev = ch['content']
            sim = float(V._semantic_similarity(claim, ev))
            if sim < V.SIMILARITY_GATE:
                per.append(dict(sim=sim, gated=1)); continue
            p = V._nli_scores(claim, ev, granularity=GRAN)
            ent = V._entity_match(claim, ev); neg = V._negation_check(claim, ev)
            c = float(p[V._NLI_CONTRADICTION]); e = float(p[V._NLI_ENTAILMENT])
            comb = 0.0 if c > V.CONTRADICTION_THRESH else 0.30 * sim + 0.70 * e
            if ent.fired: comb *= ent.score
            if neg.fired: comb *= neg.score
            per.append(dict(sim=sim, gated=0, c=c, e=e, comb=float(comb),
                            src=ch['source_file']))
        rows.append(dict(claim=claim, chunks=per))
    out.write(json.dumps(dict(qid=rec['question_id'], claims=rows)) + '\n')
    if n % 40 == 0: print(f'  {n}/{len(recs)} ({n/(time.time()-t0):.1f}/s)', flush=True)
out.close()
print('done')
