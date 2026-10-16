# Category 4 — Claim Decomposition & Atomic Fact Verification

**Supports:** Objective 2, Contribution 2, Module 1 (`decomposer.py`)
**Prior state:** **zero citations.** Claim decomposition is central to Objective 2 and
Contribution 2 and was cited to nobody anywhere in the project.

This is now well-covered, and one finding changes a design argument rather than just
filling a hole.

**Domain ladder:** no manufacturing-domain claim-decomposition work exists. The medical
tier **does** have one (MedScore, §4.5), which is useful precedent for domain adaptation.
General NLP supplies the rest. Two of the five are 2024+; FActScore (2023) is the origin
paper and cannot be replaced.

---

## 4.1 FActScore — the origin of atomic-fact decomposition

| Field | Value |
|---|---|
| Title | FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation |
| Authors | Sewon Min; Kalpesh Krishna; Xinxi Lyu; Mike Lewis; Wen-tau Yih; Pang Wei Koh; Mohit Iyyer; Luke Zettlemoyer; Hannaneh Hajishirzi |
| Venue | Proceedings of EMNLP 2023, **pp. 12076–12100** |
| DOI | `10.18653/v1/2023.emnlp-main.741` |
| arXiv | 2305.14251 |
| Status | **PUBLISHED**, peer-reviewed |
| Provenance | Crossref + arXiv API, fetched 2026-10-13 |
| Access | metadata verified; `[search snippet]` for content |

The standard citation for decomposing generated text into atomic facts and scoring each
against evidence. **This is the paper Objective 2 should cite**, and the one RAGAS's
faithfulness metric descends from.

### Role
**Support.** The foundational citation for Module 1.

---

## 4.2 VeriScore — decomposition for *verifiable* claims

| Field | Value |
|---|---|
| Title | VeriScore: Evaluating the factuality of verifiable claims in long-form text generation |
| Authors | Yixiao Song; Yekyung Kim; Mohit Iyyer |
| Venue | Findings of the ACL: EMNLP 2024, **pp. 9447–9474** |
| DOI | `10.18653/v1/2024.findings-emnlp.552` |
| arXiv | 2406.19276 |
| Status | **PUBLISHED**, peer-reviewed. **2024+ compliant** |
| Provenance | Crossref + arXiv API, fetched 2026-10-13 |
| Access | metadata verified |

Extends FActScore by distinguishing claims that are *verifiable* from those that are not.
Relevant to a real property of the thesis's data: not every sentence in a manufacturing
safety answer is a checkable factual claim — some are procedural framing or hedging. If
`decomposer.py` emits non-verifiable units, this is the citation for why that matters and
how others handle it.

---

## 4.3 SAFE — decomposition at scale

| Field | Value |
|---|---|
| Title | Long-form factuality in large language models |
| Authors | Jerry Wei; Chengrun Yang; Xinying Song; Yifeng Lu; Nathan Hu; Jie Huang; + 6 more (12 total) |
| Venue | NeurIPS 2024 (per arXiv comment) |
| arXiv | 2403.18802 — 72 pages, 18 figures, 30 tables |
| Status | NeurIPS 2024; **confirm the proceedings citation** for page numbers |
| Provenance | arXiv API, fetched 2026-10-13 |
| Access | metadata verified |

The Search-Augmented Factuality Evaluator. Cite alongside FActScore and VeriScore to
establish decompose-then-verify as standard practice rather than a bespoke choice.

---

## 4.4 DnDScore — the finding that changes an argument

| Field | Value |
|---|---|
| Title | DnDScore: Decontextualization and Decomposition for Factuality Verification in Long-Form Text Generation |
| Authors | **Miriam Wanner**; Benjamin Van Durme; Mark Dredze |
| arXiv | 2412.13175 (2024-12-17) |
| Status | **PREPRINT** — no DOI, no journal ref |
| Provenance | arXiv API, fetched 2026-10-13 |
| Access | `[search snippet]` — **recommended for a full read in Phase 2** |

This is the Wanner et al. work the project's notes wanted for "decomposition
granularity". It identifies a genuine tension the thesis has not addressed.

Reported findings `[search snippet]`, **not yet verified against the paper**:

- Decomposition can **strip the context needed to interpret a claim** — their example is
  a subclaim where "He" loses its referent.
- Decontextualization fixes that but makes the claim **less atomic**, so it becomes
  unclear which part needs verifying.
- FActScore-style verification can differ by roughly **13 percentage points** on the same
  generations depending on decomposition strategy.

### Why this matters to this thesis specifically

That 13-point sensitivity is a direct threat to the verifier's measured numbers, and it
is the kind of methodological question Dr. Maier has already shown he asks. The honest
response is not to hide it: cite it, state the decomposition strategy `decomposer.py`
uses, and acknowledge the sensitivity as a limitation in Chapter 6.

It also bears on a known bug class in the project — the "supported, but by TWO chunks"
case (Break #1b in the September plan). A claim that cannot be verified against any single
chunk may be a decontextualization artifact rather than a retrieval failure.

⚠ **Verify the 13-point figure against the paper before citing it.** It comes from a
search summary.

### Role
**Support** for the decomposition design, and a **limitation** citation for Chapter 6.

---

## 4.5 MedScore — the domain-adaptation precedent

| Field | Value |
|---|---|
| Title | MedScore: Generalizable Factuality Evaluation of Free-Form Medical Answers by Domain-adapted Claim Decomposition and Verification |
| Authors | Heyuan Huang; Alexandra DeLucia; Vijay Murari Tiyyala; Mark Dredze |
| Venue | Findings of the ACL: ACL 2026, **pp. 14149–14180**, San Diego |
| DOI | `10.18653/v1/2026.findings-acl.693` |
| arXiv | 2505.18452 |
| Status | **PUBLISHED**, peer-reviewed. **2024+ compliant** |
| Provenance | arXiv API (DOI and journal-ref present on the record), fetched 2026-10-13 |
| Access | metadata verified |

**The most strategically useful paper in this category.** It is *domain-adapted* claim
decomposition in a safety-critical domain — exactly the move this thesis makes for
manufacturing. Its existence establishes that adapting decomposition to a domain is a
recognised contribution, not an implementation detail.

Its arXiv comment also notes it "Added generalizability experiment and examples on
non-medical free-form answer", which means it offers a template for the generalisability
argument Chapter 6 will need.

### Role
**Support** and **positioning**. The closest methodological analogue in the medical tier
of the domain ladder.

---

## 4.6 Recent decomposition-quality work — optional

| Paper | Authors | arXiv | Status | Relevance |
|---|---|---|---|---|
| DecMetrics: Structured Claim Decomposition Scoring for Factually Consistent LLM Outputs | Minghui Huang | 2509.04483 | preprint | proposes COMPLETENESS, CORRECTNESS, SEMANTIC ENTROPY for scoring decomposition quality. Could be used to defend `decomposer.py`'s output quality |
| TriQua: Reconciling Granularity and Context in Factuality Evaluation | Jin Liu; Steffen Thoma; Achim Rettinger | 2608.05228 | preprint | argues for mixing granularity levels rather than a single atomic standard |

Both are unreviewed preprints. Useful if a reviewer presses on decomposition quality;
not required.

**Also noted:** the project's prior work mentions **ClaimScore (Wanner et al., 2024)**,
cited second-hand by DecMetrics as a measure of decomposition quality. This may be a
*separate* Wanner paper from DnDScore. **Unresolved** — flagged in `unverified.md`.

---

---

## 4.7 Cross-reference — atomic decomposition with NLI

Everything above concerns decomposition where verification is performed by an **LLM judge**
(the FActScore lineage). A separate sub-literature decomposes the **hypothesis** and runs
**NLI** on each atom — which is this thesis's actual mechanism, since a claim is the
hypothesis and a chunk is the premise.

→ **See `05-nli-factual-consistency.md` §5.7**, Srikanth & Rudinger (NAACL 2025,
`2502.08080`). It is filed under NLI because the finding concerns entailment-model
behaviour, but it is equally a decomposition paper and is the citation that covers both
halves of Objective 2.

## Summary for Chapter 2

Objective 2 and Contribution 2 now have a citation chain:

> Decomposing generated text into atomic verifiable units before checking each against
> evidence follows FActScore (Min et al., 2023) and subsequent work extending it to
> verifiable-claim filtering (Song et al., 2024) and large-scale evaluation (Wei et al.,
> 2024). Wanner et al. (2024) show that verification outcomes are sensitive to
> decomposition strategy, reporting differences of around 13 percentage points on
> identical generations, and identify a tension between atomicity and the context needed
> to interpret a claim. Domain adaptation of this pipeline has precedent in medical
> question answering (Huang et al., 2026). This thesis adapts decompose-then-verify to
> manufacturing safety procedural text, where claims are predominantly numerical
> thresholds and conditional requirements.

⚠ **But remember the RT4CHART finding.** Claim-level decomposition of a generated answer
against retrieved context is no longer distinctive on its own — see
`13-closest-prior-work.md`. Contribution 2's distinction must rest on the claim labels
*governing delivery*, not on the decomposition itself.
