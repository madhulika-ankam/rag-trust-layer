# Category 5 — NLI-Based Factual Consistency Verification

**Supports:** Objective 2, Contribution 3, Module 3 (`verifier.py`), the verifier-validation
protocol answering Dr. Maier
**Prior state:** one source — Explain-RAG [10] — for the entire area. SummaC, TRUE,
FactCC, Sentence-BERT, SNLI, MultiNLI and DeBERTaV3 were all on the reading list and
**none appeared in any reference list.**

All are now resolved. **The most important single fix: the thesis cites DeBERTa for a
model it does not run.**

**Domain ladder:** no manufacturing-specific NLI model or evaluation exists — the project
already established this, and it remains true. All foundations are general NLP and
necessarily pre-2024; MiniCheck and the two RAG detectors supply the recent tier.

---

## 5.1 ⚠ The model citation error — fix this first

The verifier runs `cross-encoder/nli-deberta-v3-base` (and `-large`). The project cites
**DeBERTa** `2006.03654` for it. That is the wrong paper — DeBERTaV3 is a separate work
with a different pre-training method.

| | Cite as |
|---|---|
| **DeBERTa** | Pengcheng He; Xiaodong Liu; Jianfeng Gao; Weizhu Chen — *DeBERTa: Decoding-enhanced BERT with Disentangled Attention*, arXiv `2006.03654`. ICLR 2021. **Authors in `citations.md`** |
| **DeBERTaV3** ← the model actually used | **Pengcheng He; Jianfeng Gao; Weizhu Chen** — *DeBERTaV3: Improving DeBERTa using ELECTRA-Style Pre-Training with Gradient-Disentangled Embedding Sharing*, arXiv **`2111.09543`** (2021-11-18) |
| Provenance | arXiv API, fetched 2026-10-13 |

Cite **both**: DeBERTa for the architecture lineage, DeBERTaV3 for the model instantiated.
Note the author lists differ — Xiaodong Liu is on DeBERTa but not DeBERTaV3.

⚠ Neither arXiv record carries a DOI or journal reference. The project's reading list
asserts "DeBERTa — He et al., ICLR 2021" and "DeBERTaV3 — He et al., ICLR 2023"; **the ICLR
venues are not confirmed from these records.** Verify against OpenReview before citing a
venue.

---

## 5.2 The NLI training data — now citable

Both were on the reading list and absent from every reference list. The relevance is
specific: these corpora determine what the verifier has and has not learned, which is the
mechanism behind category 6's negation finding.

| Dataset | Verified citation | arXiv |
|---|---|---|
| **SNLI** | Samuel R. Bowman; Gabor Angeli; Christopher Potts; Christopher D. Manning — *A large annotated corpus for learning natural language inference*. EMNLP 2015 (arXiv comment), **pp. 632–642** per RT4CHART's bibliography | `1508.05326` |
| **MultiNLI** | Adina Williams; Nikita Nangia; Samuel R. Bowman — ⚠ **the paper's title is *A Broad-Coverage Challenge Corpus for Sentence Understanding through Inference*.** "MultiNLI" / "MNLI" is the dataset name, not the title. NAACL 2018 per the project's reading list — **venue unconfirmed from the arXiv record** | `1704.05426` |

Cite these where §1.5 or Chapter 4 states what the entailment model was trained on. The
link to make explicit: **SNLI contains negation in 1.19% of sentences** (Hossain et al.,
category 6) — that is why negation detection is a separate mechanism rather than something
the NLI model handles.

---

## 5.3 Semantic similarity — Sentence-BERT

| Field | Value |
|---|---|
| Title | Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks |
| Authors | Nils Reimers; Iryna Gurevych |
| arXiv | 1908.10084 — arXiv comment: "Published at EMNLP 2019" |
| Status | EMNLP 2019 — the project's reading list already ticked this ✓, but it appeared in no reference list |
| Provenance | arXiv API, fetched 2026-10-13 |

The citation for the semantic-similarity mechanism and for the `all-MiniLM-L6-v2` /
`all-mpnet-base-v2` embedding models, which are used throughout the project **without any
citation at all**.

---

## 5.4 The verifier-validation protocol — SummaC and TRUE

This is the answer to "on what basis are these numbers?" for the *verifier*, as distinct
from the decision layer (category 7).

### SummaC

| Field | Value |
|---|---|
| Title | SummaC: Re-Visiting NLI-based Models for Inconsistency Detection in Summarization |
| Authors | Philippe Laban; Tobias Schnabel; Paul N. Bennett; Marti A. Hearst |
| Venue | *Transactions of the Association for Computational Linguistics* **10, pp. 163–177** |
| DOI | `10.1162/tacl_a_00453` |
| Date | 2022-02-09 |
| Status | **PUBLISHED**, peer-reviewed |
| Provenance | Crossref + arXiv `2111.09525`, fetched 2026-10-13 |

The protocol it establishes, as recorded in the project: **balanced accuracy primary,
ROC-AUC secondary, thresholds selected on a validation set, bootstrap resampling for
significance.** That is exactly the experiment design already run on the 302-pair
perturbation set.

It also supplies the balanced-accuracy definition and, critically, cites **Brodersen et
al. (2010)** for the metric itself — a secondary citation the thesis should pick up.
⚠ Brodersen et al. remains **unresolved**; see `unverified.md` §A.

**What to read:** the evaluation section only. Skip the model architecture — the project's
prior work was explicit about this.

### TRUE

| Field | Value |
|---|---|
| Title | TRUE: Re-evaluating Factual Consistency Evaluation |
| arXiv | 2204.04991 |
| Status | **ACCEPTED at NAACL 2022** — arXiv comment: "Accepted as a long paper to NAACL 2022 main conference". No DOI on the record; confirm the Anthology citation |
| Note | the project had this as "Honovich et al., 2022" with the **venue never confirmed**. Now confirmed as NAACL 2022 |
| Provenance | arXiv API, fetched 2026-10-14 |
| Access | metadata verified |

Contributes **example-level ROC-AUC over binary support labels**, and argues against
system-level correlation as an evaluation. The second half of the meta-evaluation protocol.

### The defensive line this enables

Already drafted in the project and worth keeping verbatim:

> "I follow the meta-evaluation protocol established by SummaC and TRUE for verifier
> validation and the selective-prediction protocol from SABER and the risk-coverage
> literature for the decision layer. The protocols are established; the measurements are
> mine, because the system is mine."

---

## 5.5 Comparison verifiers — what else could have been used

Each of these is a plausible alternative to the NLI cascade. Naming them pre-empts "why
not X?" and they are candidates for the LLM-judge comparison configuration in the revised
Objective 4.

| System | Verified citation | Status |
|---|---|---|
| **FactCC** | Wojciech **Kryściński**; Bryan McCann; Caiming Xiong; Richard Socher — *Evaluating the Factual Consistency of Abstractive Text Summarization*, arXiv `1910.12840` (2019-10-28) | preprint record; commonly cited as EMNLP 2020. ⚠ note the **diacritics** in the surname — the project's reading list spells it "Kryscinski" |
| **AlignScore** | Yuheng Zha; Yichi Yang; Ruichen Li; Zhiting Hu — *AlignScore: Evaluating Factual Consistency with a Unified Alignment Function*, arXiv `2305.16739`, ACL 2023 (arXiv comment), **pp. 11328–11348** per RT4CHART | published |
| **MiniCheck** | Liyan Tang; Philippe Laban; Greg Durrett — EMNLP 2024, **pp. 8818–8847**, DOI `10.18653/v1/2024.emnlp-main.499` | **PUBLISHED**, 2024+ compliant |
| **LettuceDetect** | Kovács & Recski (2025), arXiv `2502.17125` — RAG-specific hallucination detection framework | preprint |
| **Lynx** | Ravi, Mielczarek, Kannappan, Kiela & Qian (2024), arXiv `2407.08488` — open-source hallucination evaluation model | preprint |

**MiniCheck is the one to foreground.** Peer-reviewed, 2024, and explicitly about
*efficient* fact-checking on grounding documents — the same efficiency argument this thesis
makes for using a small local NLI model instead of an LLM judge.

---

## 5.6 Explain-RAG — the existing citation, now complete

| Field | Value |
|---|---|
| Title | Explain-RAG: An Explainable RAG Framework with Chain-of-Thought Reasoning, NLI Verification, and Source Attribution |
| Authors | Sahil Nadaf; Umesh B. Chavan |
| Venue | 2025 IEEE 4th International Conference for Advancement in Technology (ICONAT), **pp. 1–7** |
| DOI | `10.1109/ICONAT66879.2025.11362770` |
| Date | 2025-09-19 |
| Status | **PUBLISHED**, peer-reviewed (IEEE) |
| Provenance | Crossref, fetched 2026-10-13 |

Ref [10] was already correct; it now has **page numbers (1–7)** and a confirmed date.

One differentiator the project established and should keep: Explain-RAG uses
**BART-MNLI**, not DeBERTa, and applies NLI at whole-answer level. Both are concrete,
checkable distinctions.

---

---

## 5.7 Atomic hypothesis decomposition — the closest match to your actual mechanism

Added 2026-10-14 on request.

| Field | Value |
|---|---|
| Title | **NLI under the Microscope: What Atomic Hypothesis Decomposition Reveals** |
| Authors | Neha Srikanth; Rachel Rudinger |
| Venue | **NAACL 2025** (per arXiv comment: "Accepted to NAACL 2025") |
| arXiv | 2502.08080 — v1 2025-02-12, v2 2025-03-07 |
| Status | **ACCEPTED at NAACL 2025** — peer-reviewed. No DOI on the arXiv record, so confirm the ACL Anthology citation for page numbers. **2024+ compliant** |
| Provenance | arXiv API, fetched 2026-10-14 |
| Access | `[abstract only]` — ⚠ not yet read in full |

### Why it belongs in this category rather than category 4

Category 4 covers decomposition where verification is performed by an **LLM judge** — the
FActScore lineage. This paper decomposes the **hypothesis** into atoms and then runs
**NLI** on each one.

That is this thesis's construction exactly: a claim is the hypothesis, a retrieved chunk
is the premise, and the verifier evaluates each claim-chunk pair independently. Of
everything in this review, it is the **closest published instance of the mechanism
`verifier.py` implements.**

### What it reports

Verbatim `[abstract only]`:

> "We use **atomic decomposition of hypotheses** in two natural language reasoning tasks,
> traditional NLI and defeasible NLI, to form **atomic sub-problems**, or granular
> inferences that models must weigh when solving the overall problem."

> "Our results indicate that **LLMs still struggle with logical consistency on atomic NLI
> and defeasible NLI sub-problems.**"

> "we identify **critical atomic sub-problems** of defeasible NLI examples, or those that
> most contribute to the overall label, and propose a method to measure the **inferential
> consistency** of a model, a metric designed to capture the degree to which a model makes
> consistently correct or incorrect predictions about the same fact under different
> contexts."

### Three uses, in order of value

**1. It names a bug you already found.** "Inferential consistency — the degree to which a
model makes consistently correct or incorrect predictions about the same fact under
different contexts" is the **Break #1b** case from the September plan: a claim supported by
two chunks and scored differently against each. You diagnosed that from your own data; this
paper formalises it and proposes a measurement. That turns a bug note into a named,
published phenomenon you can cite in Chapter 6 — and, if you want, measure.

**2. "Critical atomic sub-problems" is your open scorer question.** They identify which
atoms contribute most to the overall label. Open design decision #2 — whether the trust
score should be `mean × (1 − bad_fraction)`, a soft penalty, or a min/mean blend — is the
same question asked differently: how much should one unsupported claim dominate the whole?
This is prior work on it, and worth reading before settling that decision.

**3. It is the citation Objective 2 has been missing.** Objective 2 pairs claim-level
decomposition with NLI-based verification. Until now the decomposition half was cited to
the LLM-judge literature (category 4) and the NLI half to SummaC and TRUE (§5.4), with
nothing covering the combination. This covers it, peer-reviewed and recent.

### What to read

- The abstract and the atomic sub-problem construction
- The **inferential consistency** metric definition — the directly reusable part
- The critical-sub-problem identification method
- **Worth a look despite seeming off-topic:** the defeasible-NLI sections. Defeasible
  reasoning concerns inferences that can be *overturned by new information*, which is
  conceptually close to the conditional-exception language ("required unless X", "except
  when") that the negation mechanism exists to catch. There may be a usable framing there
  for Contribution 3 — see `06-numerical-negation-nli.md`.
- **Skip:** benchmark-diversity measurement, unless defending the 161-question set's
  coverage.

### Role

**Support** for Objective 2 and Contribution 2, and a **limitation** citation for Chapter 6
on inferential consistency across chunks.

⚠ `[abstract only]`. Every characterisation above comes from the abstract. Read the paper
before quoting anything beyond the three passages above, and before relying on the
inferential-consistency metric definition.

---

## 5.8 Stacey et al. — faithfulness by construction

Added 2026-10-14.

| Field | Value |
|---|---|
| Title | **Atomic Inference for NLI with Generated Facts as Atoms** |
| Authors | Joe Stacey; Pasquale Minervini; Haim Dubossarsky; Oana-Maria Camburu; Marek Rei |
| Venue | **EMNLP 2024** — arXiv comment: "Accepted at EMNLP 2024" |
| arXiv | 2305.13214 — v1 2023-05-22, v2 2024-10-01 |
| Status | **ACCEPTED at EMNLP 2024**, peer-reviewed. No DOI on the arXiv record; confirm the ACL Anthology citation for page numbers. **2024+ compliant** |
| Provenance | arXiv API, fetched 2026-10-14 |
| Access | `[abstract only]` |

### The argument Contribution 5 is missing

Verbatim `[abstract only]`:

> "With recent advances, neural models can achieve human-level performance on various
> natural language tasks. However, **there are no guarantees that any explanations from
> these models are faithful, i.e. that they reflect the inner workings of the model.
> Atomic inference overcomes this issue, providing interpretable and faithful model
> decisions.** This approach involves making predictions for different components (or
> atoms) of an instance, before using **interpretable and deterministic rules to derive
> the overall prediction based on the individual atom-level predictions.**"

**This is the strongest single addition to Contribution 5.** The transparency report is
currently defended on *usefulness* — three layers for three audiences. It is not defended
on **faithfulness**, and faithfulness is the question the explainability literature
actually asks: why should anyone believe the explanation describes how the decision was
really made, rather than being plausible prose generated afterwards?

Stacey et al. give the answer, and it applies to this architecture directly: because the
trust score is *computed* from the per-claim verdicts by deterministic rules, the
explanation is not a reconstruction of the decision — it **is** the decision. Faithfulness
comes free from the architecture.

That reframes Contribution 5 from "we show the user helpful things" to "the explanation is
faithful by construction", which is a materially stronger claim and one with published
grounding.

**Secondary use:** it is also precedent for the scorer. Deterministic aggregation over
atom-level NLI predictions is a published method, not an ad-hoc choice — relevant to open
design decision #2.

⚠ **It decomposes premises, not hypotheses** — the mirror of this thesis's setup. The
faithfulness and aggregation arguments transfer; the specific results do not. Say so.

### What to read
The abstract, the atomic-inference framing, and the aggregation-rules section.
**Skip:** the multi-stage fact-generation training regime — that is their contribution, not
a method this thesis needs.

### Role
**Support** for Contribution 5 (faithfulness) and the scorer design.

---

## 5.9 ⚠ Atomic-SNLI — a counter-consideration, not support

Added 2026-10-14. **Do not cite this as though it helps the argument.**

| Field | Value |
|---|---|
| Title | Atomic-SNLI: Fine-Grained Natural Language Inference through Atomic Fact Decomposition |
| Authors | Minghui Huang (single author) |
| arXiv | 2601.06528 (2026-01-10, v1 only) |
| Status | **PREPRINT** — no DOI, no venue, no acceptance wording |
| Provenance | arXiv API, fetched 2026-10-14 |
| Access | `[abstract only]` |

Verbatim `[abstract only]`:

> "While atomic-level NLI offers a promising alternative by decomposing hypotheses into
> individual facts, we demonstrate that **the conventional assumption that a hypothesis is
> entailed only when all its atomic facts are entailed fails in practice due to models'
> poor performance on fine-grained reasoning.** Our analysis reveals that **existing models
> perform substantially worse on atomic level inference compared to sentence level
> tasks.**"

### Why it is here

Contribution 2 argues claim-level verification is preferable to Explain-RAG's answer-level
approach. This paper reports that atomic-level NLI is *less accurate* than sentence-level.
An examiner who knows this literature could raise it. Better to have addressed it.

### Why not to over-weight it — three reasons

1. **It is weak evidence.** Single-author preprint, January 2026, no venue, v1 only.
2. **Its atoms may not be your claims.** It decomposes SNLI hypotheses into sub-sentence
   facts. This thesis decomposes a generated answer into propositions checked against a
   retrieved chunk. Different granularity, different data, different task — the reported
   penalty may not transfer.
3. **You have your own measurements.** The 302-pair perturbation run and the 161-question
   evaluation speak to this verifier's claim-level accuracy directly. No published paper
   describes this system.

### The response to prepare

> Claim-level verification is not claimed to improve per-decision accuracy. It
> **localises** the decision: answer-level entailment indicates that an answer is
> problematic, whereas claim-level entailment identifies which statement is unsupported,
> which is what makes per-claim attribution and a graded delivery decision possible. A
> trade-off between granularity and per-decision accuracy has been reported in
> concurrent work on atomic-level inference (Huang, 2026); the cascade's rule-based
> mechanisms exist in part to offset it, and the measured performance of this
> configuration is reported in Chapter 5.

That is a stronger position than claiming accuracy superiority, and it explains why
Contribution 3 exists rather than treating it as an add-on.

**Also usable:** its aggregation rule — entailment iff *every* atom is entailed, one
contradicting atom yields contradiction, a neutral atom with no contradiction yields
neutral — is a concrete published alternative to position the scorer's soft averaging
against.

### Role
**Differentiate-from** / **limitation**. Chapter 2 and Chapter 6, not Chapter 1.

---

## 5.10 JEDI — the distribution-shift exposure

Added 2026-10-14.

| Field | Value |
|---|---|
| Title | **Extractive Fact Decomposition for Interpretable Natural Language Inference in one Forward Pass** (JEDI) |
| Authors | Nicholas Popovič; Michael Färber |
| Venue | EMNLP 2025 — arXiv comment reads "EMNLP 2025" with no acceptance wording; **confirm** |
| arXiv | 2509.18901 (2025-09-23) |
| Status | **VENUE CLAIMED** in the arXiv comment — treat as peer-reviewed only once confirmed |
| Provenance | arXiv API, fetched 2026-10-14 |
| Access | `[abstract only]` |

Verbatim `[abstract only]`:

> "existing methods rely on **resource-intensive generative large language models (LLMs)**
> to perform decomposition. We propose JEDI, an encoder-only architecture that jointly
> performs extractive atomic fact decomposition and interpretable inference **without
> requiring generative models during inference.**"

> "Experimental results demonstrate that JEDI achieves competitive accuracy in distribution
> and **significantly improves robustness out of distribution and in adversarial
> settings** over models based solely on extractive rationale supervision."

### The real reason to include it

The encoder-only efficiency point is useful but not essential — that argument can be made
without a citation.

**What earns it a place is the out-of-distribution finding, because it names this thesis's
quietest exposure.** The verifier runs `cross-encoder/nli-deberta-v3-base`, trained on
SNLI and MNLI — general-domain, crowd-sourced text. It is applied to OSHA regulations,
OSHA technical documents, NIOSH alerts and OEM manuals. That is textbook distribution
shift, and **nothing in Chapter 1 or the current reference list acknowledges it.**

If asked "how do you know your entailment model works on regulatory language?", the only
present answer is the thesis's own results. JEDI does not solve that, but it establishes
OOD robustness in NLI as a recognised problem with published work addressing it — which
allows the limitation to be named competently in Chapter 6 instead of being discovered in
a viva.

Pair it with Desai & Durrett (`08-calibration-thresholds.md` §8.2), which examines
in-domain versus out-of-domain calibration for pre-trained transformers. Together they
cover the distribution-shift question from both the accuracy and the calibration side.

### Role
**Support** for the cost/locality argument; **limitation** citation for distribution shift.

⚠ **New gap identified:** domain adaptation and distribution shift for NLI on technical or
regulatory text is not covered anywhere else in this review. Recorded in `unverified.md`.

## Summary for Chapter 2

Four actions, in priority order:

1. **Add DeBERTaV3 `2111.09543`** and stop citing DeBERTa alone for the model being run.
   This is a factual error in the current draft.
2. **Add SummaC (TACL) and TRUE** as the verifier-validation protocol. This is half the
   answer to Dr. Maier and currently appears in no reference list.
3. **Add Sentence-BERT** for the similarity mechanism and the MiniLM/mpnet models.
4. **Add SNLI and MultiNLI**, and state the link to the negation finding in category 6 —
   the training data explains the failure mode the rule-based mechanisms exist to cover.

5. **Add Srikanth & Rudinger (2025)** (§5.7) for Objective 2 — the combination of atomic
   hypothesis decomposition with NLI, which until now had no citation covering both halves.
6. **Add Stacey et al. (2024)** (§5.8) to Contribution 5 — it converts the transparency
   claim from usefulness to **faithfulness by construction**, which is the stronger claim.
7. **Address Huang (2026)** (§5.9) in Chapter 2 and Chapter 6 — the granularity/accuracy
   trade-off, answered by reframing Contribution 2 around localisation.
8. **Name the distribution-shift limitation** (§5.10) in Chapter 6, citing JEDI and
   Desai & Durrett. A general-domain NLI model is being applied to regulatory text and
   this is currently unacknowledged.

Then name FactCC, AlignScore and MiniCheck once each as alternatives considered.
