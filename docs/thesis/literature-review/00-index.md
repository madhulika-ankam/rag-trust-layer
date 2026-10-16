# Literature Review — Index

Built 2026-10-13 for the thesis *A Trust and Transparency Layer for RAG Systems,
demonstrated in manufacturing safety*.

**What this is:** verified source material and per-category structure for Chapter 2 and
for the Chapter 1 citation repairs. It is not Chapter 2 prose.

---

## How to read it

| Start here if you want… | File |
|---|---|
| **the finding that changes your contributions** | `13-closest-prior-work.md` |
| your Chapter 1 reference repairs, ready to apply | `unverified.md` §F |
| every verified citation in one place | `citations.md` |
| what is still not confirmed | `unverified.md` |

---

## The categories

| # | Category | Prior state | Now |
|---|---|---|---|
| 1 | [Manufacturing & Industrial RAG](01-manufacturing-rag.md) | 2 real, 2 placeholders | **rebuilt 2026-10-15**: 11 of 12 now peer-reviewed journal/conference papers, incl. the benchmark itself (*Manufacturing Letters*). ⚠ gap claim needs re-testing — §1.8 |
| 2 | [Safety-Critical & High-Stakes AI](02-safety-critical-ai.md) | **empty** | anchored on an ATC paper whose failure modes are your perturbation types |
| 3 | [Hallucination Taxonomies](03-hallucination-taxonomies.md) | strongest area | both unresolved survey IDs found; one is peer-reviewed TOIS |
| 4 | [Claim Decomposition](04-claim-decomposition.md) | **uncited** | FActScore lineage + a 13-point sensitivity finding you need to own |
| 5 | [NLI Factual Consistency](05-nli-factual-consistency.md) | 1 source for the whole area | 15 resolved, **including the DeBERTaV3 error fix**; §5.7–5.10 added 2026-10-14 |
| 6 | [Numerical & Negation in NLI](06-numerical-negation-nli.md) | **uncited** | now the best-supported claim in the thesis |
| 7 | [Selective Prediction & Abstention](07-selective-prediction.md) | field never named | named, differentiated, four metrics each sourced |
| 8 | [Calibration & Thresholds](08-calibration-thresholds.md) | **uncited** | the three-part answer to Dr. Maier |
| 9 | [Transparency & Attribution](09-transparency-attribution.md) | **uncited** | AIS framework + the post-hoc attribution distinction |
| 10 | [Trust Calibration & Over-Reliance](10-trust-calibration.md) | 1 placeholder preprint | Lee & See (2004) + two surveys |
| 11 | [RAG Evaluation Frameworks](11-rag-evaluation-frameworks.md) | RAGAS uncited | RAGAS + ARES + LLM-judge validity |
| 12 | [Benchmark & Perturbation](12-benchmark-perturbation.md) | **BUMP had no ID anywhere** | BUMP resolved: ACL 2023, `2212.09955` |
| 13 | [Closest Prior Work](13-closest-prior-work.md) | 1 of 3 triaged | all 3 triaged; headline survives but narrows |

---

## The three findings that matter most

**1. RT4CHART (`2603.27752`) overlaps Contributions 2 and 5.** It decomposes the generated
answer into claims, labels each against retrieved context, maps them to answer spans and
returns the evidence — post-hoc. Your answer-vs-query distinction does not separate you
from it. **What saves you:** it never withholds anything. Zero occurrences of abstain,
withhold, refuse, deliver or gate in the full text. Your remaining novelty is the
conjunction of post-hoc answer-level verification *with* delivery gating, which neither
competitor has. Contributions 2 and 5 need rewording.

**2. Your weakest claim became your strongest.** "Entailment models are known to be weak on
numbers and conditional exceptions" was uncited. EQUATE reports nine NLI models failing to
beat a majority-class baseline on quantitative reasoning, with a symbolic quantity handler
beating the best neural model by +24.2% on numerical reasoning and losing 8.1% on verbal.
That is your cascade, published in 2019. Hossain et al. report negation in 1.19% of SNLI
against ~25% of general English, with transformers scoring below the majority baseline on
negation-critical pairs.

**3. Two whole fields your design sits inside were never named.** The decision module *is*
selective prediction (El-Yaniv & Wiener, 2010 — who coin "risk-coverage trade-off"), and
the weights question *is* calibration (Guo et al., 2017). Naming them costs a paragraph
each and removes the two most obvious examiner questions.

---

## Verification protocol used

| Rule | How it was enforced |
|---|---|
| No citation from memory | every reference resolved against the arXiv API or Crossref during the session |
| arXiv ID ↔ title cross-check | all IDs resolved and title-matched; **zero failures**, zero fabrications found in the existing project |
| Unverified stays unverified | missing fields marked `UNVERIFIED`; `citations.md` is **generated from API responses**, not typed |
| Quotes copied, not reconstructed | every quote tagged `[full text]`, `[abstract only]` or `[search snippet]` |
| Peer-review status recorded | published vs preprint stated for every entry |
| Date policy | 2024+ for the competitive landscape; foundational papers exempt and marked with why |

**Two papers were read in full:** RT4CHART (`2603.27752`) and Hossain et al. (2020), plus
EQUATE's abstract and findings extracted from the PDF. Everything else is metadata-verified
with abstract- or snippet-level content, marked accordingly.

---

## Corrections to the existing project

Full list in `unverified.md` §F. The ones that change text:

1. **DeBERTaV3 ≠ DeBERTa.** You cite `2006.03654` for `deberta-v3-*`. Add `2111.09543`.
2. **Ref [4] mixes two titles.** The Frontiers version is titled differently from the arXiv
   preprint. Pick one.
3. **Refs [5], [6], [7] resolved.** [5] and [6] are peer-reviewed; [7] is not, and it is the
   one carrying your trust-calibration argument.
4. **Ref [9] needed no fix** — Maynez et al.'s title was correct.
5. **`2207.05221` is "Language Models (Mostly) Know What They Know"**, not "Linguistic
   Calibration of LLMs".
6. **The "Zhang et al. 2023" survey is `2309.01219`**, *Siren's Song in the AI Ocean* — but
   still an unreviewed work in progress. Prefer Huang et al. (TOIS 2025, `2311.05232`).
7. **Ref [8] Ji et al. pagination was already correct** as `55(12), 1–38`.

---

## Recommended next steps

| Priority | Action |
|---|---|
| 1 | Reword Contributions 2 and 5 against RT4CHART before writing any Chapter 2 prose |
| 2 | Apply the Chapter 1 reference repairs from `unverified.md` §F — they are ready |
| 3 | Read in full: SABER `2605.18792`, "Can We Trust the Judges?" `2609.15561`, DnDScore `2412.13175`, RAGalyst `2511.04502` |
| 4 | Resolve Brodersen et al. (2010) — the primary citation for your headline metric |
| 5 | Chase the four journal leads in `01-manufacturing-rag.md` §1.6; the manufacturing tier is preprint-heavy |
| 6 | Get ISO 10218 / ISO/TS 15066 for the cobot safety claim |
