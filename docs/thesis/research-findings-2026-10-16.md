# Research findings — 16 October 2026

Three things in this document: papers verified against their sources today,
the four-condition experiment run on the frozen generations, and the
Category 3 hallucination taxonomy applied to this project's own outputs.

Everything here is tagged:

```
[VERIFIED]      checked against the paper or an API response today
[SNIPPET]       from a search result, NOT confirmed — do not cite
[MEASURED]      produced by a script in src/experiments/, reproducible
[PROXY]         measured, but against regex labels rather than ground truth
[UNTESTED]      a hypothesis with no evidence either way
```

---

## Part 1 — Papers verified today

### 1.1 The closest architectural relative found so far

**Facet-Level Tracing of Evidence Uncertainty and Hallucination in RAG**
Passant Elchafei, Monorama Swain, Shahed Masoudian, Markus Schedl
arXiv **2604.09174** · submitted 2026-04-10, revised 2026-05-19 · cs.CL
**PREPRINT** — no venue, no journal reference, no DOI beyond the arXiv one
`https://arxiv.org/abs/2604.09174`

**Why this matters more than anything else found today.** Their architecture
is this thesis's architecture:

| they do | this thesis does |
|---|---|
| decompose each question into atomic reasoning *facets* | decompose each answer into atomic *claims* |
| score each facet against each chunk with NLI | score each claim against each chunk with NLI |
| RoBERTa-large-MNLI, score = P(entail) − P(contradict) | DeBERTa-v3, score = 0.30·sim + 0.70·P(entail) |
| a Facet × Chunk matrix combining relevance and faithfulness | per-claim, per-chunk similarity + NLI |
| three inference modes: Strict RAG / Soft RAG / LLM-only | four prompt conditions: minimal / grounded / guarded / stress |

**[VERIFIED] their failure taxonomy, and the rates.** Five categories —
Evidence Failure, Evidence Overridden, Misalignment, Helpful, Robust — as a
percentage of facets:

| dataset | Failure | Overridden | Misalign | Helpful | Robust |
|---|---|---|---|---|---|
| Medical (11,007 facets, 1,500 questions) | 7.0 | **28.4** | 7.5 | 38.1 | 19.0 |
| HotpotQA (24,039 facets, 3,000 questions) | 5.8 | **42.3** | 0.7 | 37.6 | 13.6 |

Override — the model's prior knowledge overriding evidence it *did* retrieve
— is the dominant failure in both, roughly 4× the retrieval-failure rate on
medical and 7× on HotpotQA.

**[VERIFIED] strict grounding is often worse than no retrieval.** F1 on
medical complex reasoning:

| model | Strict RAG | Soft RAG | LLM-only |
|---|---|---|---|
| Gemini-2.0 Flash | 0.176 | 0.357 | 0.340 |
| GPT-4o mini | 0.089 | 0.161 | 0.127 |
| Llama-3-8B-Instruct | 0.226 | 0.306 | 0.306 |

Strict RAG is below LLM-only in five of six cells. Soft RAG gains on complex
reasoning are reported as +103% (Gemini), +81% (GPT), +35% (Llama).

⚠ The paper states "approximately 30%" of questions degrade under Soft RAG
in §4.3, while its summary attributes a 30% figure to strict grounding
falling below the no-retrieval baseline. **These are different claims and the
paper does not reconcile them.** If either figure is cited, read §4.3 first.

**What to do with it.** Four things:

1. **Cite it in Chapter 2 §2.9 as the closest prior work on the mechanism.**
   It is a preprint, so it does not displace the thesis — but an examiner who
   finds it and is not told about it is a problem.
2. **Adopt their five-category taxonomy for the error analysis.** It is a
   published-precedent framework for exactly the analysis Chapter 5 needs,
   and it is strictly more informative than SUPPORTED / UNSUPPORTED /
   CONTRADICTION.
3. **"Evidence Overridden" is a failure mode this thesis does not currently
   detect, and it is the dominant one in their data.** See Part 3.
4. **Their scoring rule is a free comparison.** P(entail) − P(contradict) is
   a single signed score with published precedent, and it can be computed
   from `perchunk_sentence.jsonl` without re-running NLI. It is a direct
   alternative to the hand-set 0.30/0.70 weighting.

### 1.2 Retrieval-side failure — the gap in Categories 1–4

**The Distracting Effect: Understanding Irrelevant Passages in RAG**
Chen Amiraz, Florin Cuconasu, Simone Filice, Zohar Karnin
arXiv **2505.06914** · submitted 2025-05-11
**PUBLISHED** — DOI `10.18653/v1/2025.acl-long.892` → ACL 2025, long papers
`https://arxiv.org/abs/2505.06914`

**[VERIFIED]** They formalise "the distracting effect of a passage w.r.t. a
query (and an LLM)" as a measurable quantity, arguing against treating
irrelevant passages as a single class — "completely unrelated vs.
distracting" is their distinction. Fine-tuning on mined hard distracting
passages yields **up to a 7.5% increase in answering accuracy** over
conventional RAG fine-tuning.

**Why it matters here.** This is peer-reviewed, 2025, and it fills the one
real hole in the existing review: a search of Categories 1–4 for
*irrelevant*, *distractor*, *noisy retrieval* or *misleading context*
returns nothing on topic. It also explains two measured facts in this
project:

- **`SIMILARITY_GATE = 0.25` cannot filter distractors.** A distracting
  passage is by definition semantically close to the query. The gate removes
  unrelated chunks, not misleading ones.
- **Module 4 failing at 1-of-8 off-target detection is the expected result,
  not a bug.** Relevance and distraction are different quantities; a
  similarity-based relevance check cannot separate them.

Both of those currently read as unexplained weaknesses. With this citation
they become predicted behaviour.

### 1.3 Supporting evidence that prompt-based abstention is insufficient

[SNIPPET] — already in the review at `07-selective-prediction.md`:124 but
unused: Setiawan, *Prompt-Based Abstention Fails Under Misleading Context*,
arXiv **2608.22228**. Preprint, "Committed to AACL-IJCNLP 2026", i.e. not
accepted. The notes record its finding as "prompt-based abstention *fails*,
which argues for a mechanism outside the prompt".

**This is the thesis premise, stated by someone else.** Part 2 below now
measures the same thing on this corpus. It should be cited in Chapter 1 §1.3
and Chapter 2, with its preprint status stated.

### 1.4 Found and not pursued

| paper | why not |
|---|---|
| *Disentangling Faithfulness Hallucinations in RAG*, Springer *Machine Learning*, DOI `10.1007/s10994-026-07121-y` | [SNIPPET] only. Published venue, worth 20 minutes for Chapter 2 if time allows |
| Stanford *Hallucination-Free? Assessing Reliability of Leading AI Legal Research Tools* | [SNIPPET]. Deployed-RAG hallucination rates in a high-stakes domain — good Chapter 1 motivation, different domain |
| *Long-Context LLMs Meet RAG*, arXiv 2410.05983 | [SNIPPET]. Hard negatives; stronger retrievers surface more convincing distractors. Overlaps 1.2 |
| GSM-DC, arXiv 2505.18761 | [SNIPPET]. Math word problems — transfer to RAG not established |
| *When Retrieval Doesn't Help*, arXiv 2606.04127 | [SNIPPET]. Biomedical, recent preprint |

**None of the numbers in this table are verified. Do not cite any of them
without reading the paper.**

---

## Part 2 — The four-condition experiment

Script: `venv/bin/python src/experiments/prompt_conditions.py`
All four conditions use the **same 161 questions** and the same retrieval
(except `stress`, which differs on 62 of 161 by design). Generations were
frozen on 13–14 October; all four were re-verified against the current
trust layer today.

### 2.1 What the generator does, and what the layer does — all 161

| condition | declined | claims | mean ent | SUPP | CONTR | ANSWER | WARN | REFUSE | ESCAL |
|---|---|---|---|---|---|---|---|---|---|
| minimal | **0** | 720 | 0.490 | 46% | 13 | 7 | 16 | 125 | 13 |
| grounded | 10 | 538 | 0.528 | 49% | 23 | 9 | 25 | 106 | 21 |
| guarded | 24 | 429 | 0.525 | 49% | 11 | 7 | 22 | 122 | 10 |
| stress | 1 | 665 | 0.517 | 48% | 18 | 8 | 21 | 114 | 18 |

**[MEASURED]** Under `minimal` the model declines **zero times out of 161**
and produces 68% more claims than under `guarded`. The abstention
instruction in the guarded prompt is doing a great deal of work.

### 2.2 The result the thesis needs — Config A versus Config D

**[PROXY]** On the **37 questions labelled ESCALATE** (the gold answer
indicates the manuals do not answer them), a substantive answer is
unsupported by construction. Without the layer every generated answer
reaches the user.

| | UNSUPPORTED delivered | | ANSWERABLE delivered | |
|---|---|---|---|---|
| condition | no layer | **with layer** | no layer | **with layer** |
| minimal | 37/37 | **3/37** | 121/121 | **20/121** |
| grounded | 36/37 | **6/37** | 112/121 | **27/121** |
| guarded | 34/37 | **4/37** | 100/121 | **24/121** |
| stress | 37/37 | **3/37** | 120/121 | **25/121** |

Read the left block as the benefit and the right as the cost.

**The headline, stated honestly:** under the unguarded prompt the layer
reduces delivered unsupported answers from **37 to 3 — a 92% reduction** —
at the cost of reducing delivered answerable answers from 121 to 20.

**The comparison that makes the thesis worth doing.** Prompt-based
abstention and the verification layer are two mechanisms for the same job,
so compare their efficiency — unsupported answers caught per answerable
answer sacrificed, both measured against the `minimal` baseline:

| mechanism | unsupported caught | answerable lost | caught per answer lost |
|---|---|---|---|
| guarded prompt alone | 3 | 21 | **0.14** |
| verification layer (on minimal) | 34 | 101 | **0.34** |

The layer catches **2.4× more unsupported answers per answerable answer
sacrificed** than the prompt instruction does. Both are conservative; the
layer is the better-targeted of the two. That is a defensible contribution
and it is the direct empirical counterpart to Setiawan's argument in §1.3.

⚠ **This whole table rests on `expected_decision`, which is
regex-generated and unvalidated** — it disagrees with the author's own
reading on q23 and q139 (`facts.md` §2). It is a proxy for groundedness. The
30 hand-labelled answers remain the only ground truth, and Dr. Morkos's 20
reviewed labels are what would upgrade this from proxy to measurement.

### 2.3 The 30 hand-labelled questions across conditions

| her judgement | n | minimal | grounded | guarded | stress |
|---|---|---|---|---|---|
| fully good | 13 | 3 | 5 | **6** | 5 |
| incomplete | 6 | 0 | 0 | 0 | 0 |
| off-target | 7 | 2 | 1 | **1** | 3 |
| partly grounded | 4 | 1 | 1 | 1 | 1 |

**Her labels were made on the GUARDED answers. The other three columns are
different text for the same questions, so the labels do not transfer.** Read
this as layer *behaviour*, not accuracy. What it does show: the guarded
condition is where the layer delivers most sound answers, which is
consistent with guarded answers being shorter and better grounded.

**[MEASURED] A selection effect worth stating in Chapter 3.** Within those
30 questions the generator declined **zero** times in all four conditions,
while declining 24 times across the full 161 under `guarded`. The
hand-labelled sample contains no declines, so it cannot say anything about
how the system handles honest refusals.

---

## Part 3 — Is this system hallucinating? Category 3 applied

### 3.1 The taxonomy, from the notes

`03-hallucination-taxonomies.md` is explicit that **Ji et al.** (*ACM
Computing Surveys* 55(12):1–38, DOI `10.1145/3571730`) define exactly two
types, and that an earlier four-type framing was retracted:

- **intrinsic** — the output contradicts the source
- **extrinsic** — the output is neither supported nor contradicted by it

Two refinements the notes add: **Huang et al.** (*ACM TOIS*, DOI
`10.1145/3703155`) separate *factuality* (against the world) from
*faithfulness* (against the source); **Zhang et al.**, Siren's Song
(*Computational Linguistics* 51(4):1373–1418, DOI `10.1162/COLI.a.16`)
supply **context-conflicting** as the RAG-relevant category.

This thesis measures **faithfulness**, not factuality. It should say so
plainly: a claim the manuals do not support may still be true of the world,
and this system cannot tell the difference.

### 3.2 Applying it to this project's own outputs

| type | how it appears here | evidence |
|---|---|---|
| **intrinsic** (contradicts source) | verdict `CONTRADICTION` | **[MEASURED]** 11 of 429 claims under `guarded` (2.6%); 13/720 minimal, 23/538 grounded, 18/665 stress. **[MEASURED]** In the 30 hand-read answers the author found **zero** claims contradicting the manuals |
| **extrinsic** (unsupported) | verdict `UNSUPPORTED` | **[MEASURED]** ~51% of claims under `guarded`. **[MEASURED]** By hand, **one answer in 30** (q48) contains content the manuals do not support |
| **context-conflicting** (Zhang et al.) | the same thing as intrinsic in this setup, since the only source is the retrieved chunks | — |
| **factuality** errors | **not measurable here** | the system has no world model; out of scope and must be stated as such |

**[MEASURED] Answer: the underlying RAG generator hallucinates
extrinsically and barely at all intrinsically.** Under the guarded prompt,
one answer in thirty carries unsupported content and none contradicts the
manuals. That is a clean mapping onto Ji et al. and it is a reportable
finding, not a gap.

### 3.3 Where the trust layer itself fails

The layer is not a generator, so it cannot hallucinate. It can be wrong, and
it is, measurably:

| failure | evidence | status |
|---|---|---|
| **false rejection** — withholds sound answers | 7 of 13 hand-judged-good answers withheld; 101 of 121 answerable questions withheld under minimal | **[MEASURED]** the dominant error by a wide margin |
| **false acceptance** — delivers unsound answers | 1 of 4 partly-grounded answers delivered; 3 of 37 unanswerable questions delivered under minimal | **[MEASURED]** / **[PROXY]** |
| **false alarm** — ESCALATE on a sound answer | 0 of 13 after the 14 October rule change, down from 3 | **[MEASURED]** |
| **decomposer misrepresentation** | four splitting defects raised the contradiction count while length statistics improved | **[MEASURED]**, all fixed; see `CONTEXT.md` 2026-10-14 |

### 3.4 One hallucination type this system cannot currently detect

**Evidence Overridden** — the dominant failure in Elchafei et al., at 28–42%
of facets. The model retrieves correct evidence and then answers from its
parametric knowledge instead.

**[UNTESTED] in this project.** Whether it occurs here is unknown, and the
current verifier would only partly catch it: an overridden claim is flagged
UNSUPPORTED *if* no chunk supports it, but if the model's prior happens to
match a different retrieved chunk, the claim passes.

What would test it: for claims the layer marks UNSUPPORTED, check whether
the correct evidence *was* retrieved. If it was, the generator ignored
available evidence — override. If it was not, that is retrieval failure.
This needs no new generation, only a per-claim check of whether any
retrieved chunk contains the answer. The distinction matters because the two
have different fixes, and the thesis currently conflates them.

---

## Part 4 — What is worth doing, and what is not

Ranked by thesis value per hour, given 21 days to the defense.

### Essential

**E1. Write Part 2 into Chapter 5 as the main result.** No new work. The
92%-reduction figure and the 2.4× efficiency comparison are the answer to
"what did the layer buy", and they exist now.

**E2. Add Elchafei et al. and Amiraz et al. to Chapter 2.** ~1 hour. The
first is the closest prior work on the mechanism; the second explains two
measured weaknesses as predicted behaviour rather than defects.

**E3. Re-classify the 30 hand-read answers using the five-category
taxonomy** (Failure / Overridden / Misalignment / Helpful / Robust).
~1 hour of the author's reading. It gives Chapter 5 an error analysis with
published precedent, and it is the only way to find out whether override
occurs on this corpus.

### Worth doing if the chapters are on track

**W1. Test P(entail) − P(contradict) as the scoring rule.** ~30 minutes, no
NLI re-run — the features are in `perchunk_sentence.jsonl`. Published
precedent, and it either beats the hand-set 0.30/0.70 weighting or gives
another row for the table that answers Dr. Maier.

**W2. Retrieval-sufficiency check on UNSUPPORTED claims.** ~2 hours. Splits
retrieval failure from generation failure, per §3.4. The single largest
unexamined question in the project.

**W3. Risk–coverage curve per condition.** ~1 hour. The Part 2 table is one
operating point; the curve shows whether the layer dominates prompt-based
abstention at every point or only at this one.

### Explicitly not doing

| | why |
|---|---|
| swapping the NLI model | `-large` was tested and did not improve. Elchafei et al. use RoBERTa-large-MNLI, an *older* model, so there is no evidence a change helps |
| reranking, query reformulation, top-k or chunk-size sweeps | these change the RAG system; the thesis is about the layer above it |
| fine-tuning on mined distracting passages (Amiraz et al.'s method) | correct direction, far outside a 21-day budget. Cite it as future work |
| RAGAS (Config B) and LLM-as-judge (Config C) | only if the chapters are finished early |
| further decomposer tuning | measured return was one answer per two days |

---

## Corrections to earlier claims in this project

1. **The "4–7× override" figure** was quoted from a search snippet in my
   earlier summary. It is now **[VERIFIED]** from the paper's own tables
   (28.4% vs 7.0% medical, 42.3% vs 5.8% HotpotQA) and the paper describes
   the ratio as roughly 4× and 7×. The figure survived; the provenance did
   not, and that is the part that matters.

2. **"Nobody has studied decomposition granularity versus verification
   accuracy"** is false — DnDScore, Atomic-SNLI and TriQua are all in this
   project's own notes. The surviving claim is narrower: no published work
   reports verification accuracy as a function of claim *length*, with a
   control condition. See `facts.md` §10.

3. **`citations.md` lost its Category 14 block.** It was rewritten at 01:13
   on 16 October and BUMP's arXiv id `2212.09955` now appears zero times,
   while `unverified.md` still records those six as added. Regenerate with
   `python -m src.verify_citations --batch`.
