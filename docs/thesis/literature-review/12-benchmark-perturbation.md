# Category 12 — Benchmark Construction & Perturbation Evaluation

**Supports:** the 302-row perturbation set, RQ3, the verifier-validation experiment
**Prior state:** **BUMP was the named precedent for the entire perturbation design and had
no title, no arXiv ID and no venue anywhere in the project.** Now resolved.

**Domain ladder:** minimal-pair meta-evaluation is a general-NLP method; no manufacturing
equivalent. BUMP (2023) is the origin and cannot be replaced; RAGTruth (2024) and the
answer-perturbation work (2026) supply the recent tier.

---

## 12.1 BUMP — the precedent, finally citable

| Field | Value |
|---|---|
| Title | **BUMP: A Benchmark of Unfaithful Minimal Pairs for Meta-Evaluation of Faithfulness Metrics** |
| Authors | **Liang Ma; Shuyang Cao; Robert L. Logan IV; Di Lu; Shihao Ran; Ke Zhang; Joel Tetreault; Alejandro Jaimes** |
| Venue | **ACL 2023** — arXiv comment: "Accepted as a long main conference paper at ACL 2023" |
| arXiv | **2212.09955** (2022-12-20) |
| Status | ACL 2023 long main conference paper — **confirm the Anthology citation** for page numbers |
| Provenance | arXiv API, fetched 2026-10-13 |
| Access | metadata verified |

"Ma et al., 2023" in the project is **correct** — first author Liang Ma. The paper's own
title names the method the thesis uses: *a benchmark of unfaithful minimal pairs for
meta-evaluation of faithfulness metrics*. That is a one-line description of the 302-pair
experiment.

Recorded in the project, now attributable: BUMP contributes **889 human-written minimal
pairs, each introducing a single error from an ontology of seven types** into a reference
summary.

### How to use it, precisely

The perturbation design already mirrors BUMP: one error per pair, drawn from a typed
ontology, with the uncorrupted original kept as a positive. Three things to say in
Chapter 5:

1. **The design follows BUMP's minimal-pair protocol.** This converts the perturbation set
   from an ad-hoc construction into an instance of a published method.
2. **The error ontology is narrower and domain-motivated.** BUMP uses seven types across
   general summarisation; this thesis uses three — numerical, negation, entity swap —
   chosen because they are the failure modes that carry operational consequence in
   procedural safety text (and, per category 6, the ones NLI handles worst).
3. **The scale difference is honest.** BUMP has 889 human-written pairs; this has 302. State
   it rather than inviting the comparison.

⚠ One thing to check when reading it: whether BUMP's pairs are *human-written* throughout.
If so, and if the 302 pairs here are script-generated from gold answers, that is a
difference a reviewer may raise. Prepare the answer — script generation from
expert-validated gold answers has its own validity argument, but it must be made.

---

## 12.2 RAGTruth — the RAG-native corpus

| Field | Value |
|---|---|
| Title | RAGTruth: A Hallucination Corpus for Developing Trustworthy Retrieval-Augmented Language Models |
| Authors | Cheng Niu; Yuanhao Wu; Juno Zhu; Siliang Xu; KaShun Shum; + more |
| Venue | ACL 2024 (Volume 1: Long Papers), **pp. 10862–10878** |
| DOI | `10.18653/v1/2024.acl-long.585` |
| Status | **PUBLISHED**, peer-reviewed. 2024+ compliant |
| Provenance | Crossref, fetched 2026-10-13 |

The standard RAG hallucination corpus, and the benchmark RT4CHART evaluates on.

**Carries a caution worth reproducing.** RT4CHART's re-annotation of RAGTruth found
"1.68× more hallucination cases than the original labels, suggesting that commonly used
benchmarks substantially underestimate the prevalence of hallucination" `[full text,
RT4CHART abstract]`. That is a strong argument for this thesis's reliance on an
expert-validated benchmark — and a caution about its own label quality.

---

## 12.3 Synthetic-corruption benchmarks

| Paper | Verified citation | Status |
|---|---|---|
| **SummEdits** (in *LLMs as Factual Reasoners: Insights from Existing Benchmarks and Beyond*) | Philippe Laban; Wojciech Kryściński; Divyansh Agarwal; Alexander R. Fabbri; Caiming Xiong; Shafiq Joty; Chien-Sheng Wu — arXiv `2305.14540` (2023-05-23) | PREPRINT record, no DOI. ⚠ note the project refers to "SummEdits (Laban et al., 2023)" — SummEdits is the *benchmark* introduced in this paper, not the paper's title |
| **HaluEval** | Junyi Li; Xiaoxue Cheng; Wayne Xin Zhao; Jian-Yun Nie; Ji-Rong Wen — *HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models*, arXiv `2305.11747`. **EMNLP 2023 Main Conference (Long Paper)** per arXiv comment | published — confirm Anthology citation |

Both consist of inconsistent summaries corrupted by introducing synthetic factual errors —
the same construction logic as the perturbation set, at larger scale. Cite them with BUMP
to establish synthetic corruption as accepted practice, not a shortcut.

---

## 12.4 The most directly relevant recent paper

| Field | Value |
|---|---|
| Title | **Can We Trust the Judges? Validation of Factuality Evaluation Methods via Answer Perturbation** |
| arXiv | 2609.15561 |
| Status | PREPRINT — authors in `citations.md` |
| Access | metadata verified |

The title is almost a description of this thesis's own verifier-validation experiment:
validating factuality evaluation methods by perturbing answers. **Surfaced in prior work
and never discussed.**

**Priority read.** If it establishes answer perturbation as a validation methodology, it is
the single best methodological citation for the 302-pair experiment — more directly on
point than BUMP, which validates faithfulness *metrics* for summarisation. If it reaches
conclusions about which methods survive perturbation, those are findings this thesis should
position against.

---

## Summary for Chapter 5 methodology

> The verifier is validated using a minimal-pair protocol following BUMP (Ma et al., 2023),
> in which each pair introduces exactly one error of a known type into an otherwise
> faithful reference, allowing the contribution of each verification mechanism to be
> attributed to the failure mode it targets. Where BUMP draws from an ontology of seven
> error types across general summarisation, the ontology here is restricted to three —
> numerical substitution, negation reversal, and entity substitution — selected because
> they are the error categories that carry operational consequence in procedural safety
> text and, per Ravichander et al. (2019) and Hossain et al. (2020), the categories on
> which entailment models perform worst. Synthetic corruption of reference text is
> established practice in factual-consistency meta-evaluation (Laban et al., 2023;
> Li et al., 2023). Following SummaC (Laban et al., 2022), balanced accuracy is reported
> as the primary metric with ROC-AUC secondary, thresholds selected on a validation split
> and performance reported on a held-out test split.

That paragraph answers the methodology half of the Maier objection, with every citation
verified.
