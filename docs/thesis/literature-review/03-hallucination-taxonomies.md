# Category 3 — Hallucination in RAG and its Taxonomies

**Supports:** §1.5 (the scope statement distinguishing generation-time from delivery-time),
RQ1, Chapter 2 area 1 of three
**Prior state:** the strongest-cited area in the thesis. Two solid references, two surveys
discussed with unresolved IDs, and one retracted framing to keep out.

**Domain ladder:** taxonomies are general-NLP constructs; no manufacturing-specific
hallucination taxonomy exists or is needed. Foundational papers are pre-2024 by
necessity — this is where intrinsic/extrinsic originates. Two 2024–2025 surveys supply
the recency.

---

## 3.1 Ji et al. — the taxonomy the thesis already uses

| Field | Value |
|---|---|
| Title | Survey of Hallucination in Natural Language Generation |
| Authors | Ziwei Ji; Nayeon Lee; Rita Frieske; Tiezheng Yu; Dan Su; Yan Xu; Etsuko Ishii; Ye Jin Bang; Andrea Madotto; Pascale Fung |
| Venue | *ACM Computing Surveys* **55(12), pp. 1–38** |
| DOI | `10.1145/3571730` |
| Date | 2023-12-31 (Crossref). ⚠ the arXiv journal-ref string says "(2022)" — cite 2023 |
| arXiv | 2202.03629 (v7) |
| Status | **PUBLISHED**, peer-reviewed |
| Provenance | Crossref + arXiv API, fetched 2026-10-13 |
| Access | metadata verified; `[search snippet]` for content |

### Two settled facts to protect

1. **It defines exactly two types** — intrinsic (contradicts the source) and extrinsic
   (neither supported nor contradicted). An earlier four-type framing in the thesis
   conversation was wrong and explicitly retracted. Do not let it reappear.
2. **Task placement.** RAG is not its own category in the survey. The thesis should
   locate itself under **generative question answering**, not abstractive summarisation
   or dialogue. The survey's six tasks: abstractive summarisation, dialogue generation,
   generative QA, data-to-text, machine translation, visual-language generation.

### What to read
§2 (definitions and the intrinsic/extrinsic split) and the generative-QA task section.
**Skip:** the machine-translation and visual-language sections.

### ✅ Your ref [8] is correct — and it could easily not have been

The author-list check run on 2026-10-16 found a **real discrepancy** here, and Chapter 1
happens to be on the right side of it:

| Version | Authors |
|---|---|
| arXiv `2202.03629` **v7** | **13** — adds Delong Chen, Ho Shu Chan, Wenliang Dai |
| Published *ACM Computing Surveys* 55(12) | **10** — Ji, Lee, Frieske, Yu, Su, Xu, Ishii, Bang, Madotto, Fung |

Chapter 1's ref [8] lists the **10-author published version**, which is correct. Had it
been built from the arXiv page it would carry three authors who are not on the journal
article.

One benign note: the published record renders the eighth author as **"Ye Jin Bang"** where
arXiv has "Yejin Bang" — the same person, spaced differently. Use the published spacing.

### Role
**Support.** Correctly cited as [8], with correct pagination (`55(12), 1–38`) — see the
correction note in `unverified.md` §F.

---

## 3.2 Maynez et al. — where intrinsic/extrinsic originates

| Field | Value |
|---|---|
| Title | On Faithfulness and Factuality in Abstractive Summarization |
| Authors | Joshua Maynez; Shashi Narayan; Bernd Bohnet; Ryan McDonald |
| Venue | ACL 2020 (per arXiv comment: "ACL 2020, 14 pages") |
| arXiv | 2005.00661 |
| Status | PREPRINT record; ACL 2020 proceedings entry still needs page numbers |
| Access | metadata verified |

**The title doubt is resolved.** Chapter 1's verification note flagged the title as
needing confirmation against the ACL Anthology. The arXiv record confirms it is correct
exactly as written. No change needed.

**One adaptation to make explicit in Chapter 2.** Maynez et al. define intrinsic and
extrinsic relative to *the source document in summarisation*. The thesis applies them
relative to *retrieved chunks in RAG*. That is a reasonable transfer, but it should be
stated as a transfer rather than presented as the original definition — an examiner who
knows the paper will notice the substitution.

### Role
**Support**, cited jointly with Ji et al. as [9].

---

## 3.3 Huang et al. — the unresolved ID, now resolved

| Field | Value |
|---|---|
| Title | A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions |
| Authors | Lei Huang; Weijiang Yu; Weitao Ma; Weihong Zhong; Zhangyin Feng; Haotian Wang; + 5 more (11 total) |
| Venue | *ACM Transactions on Information Systems*, **pp. 1–55** |
| DOI | `10.1145/3703155` |
| Date | 2025-03-31 (Crossref); arXiv v1 2023-11-09, v2 2024-11 |
| arXiv | 2311.05232 |
| Status | **PUBLISHED**, peer-reviewed (ACM TOIS) |
| Provenance | Crossref + arXiv API, fetched 2026-10-13 |
| Access | `[search snippet]` |

The thesis chat recorded this as "Huang et al. (2023) — arXiv: find via search". **Now
resolved.** Note it is properly cited as a **2025** TOIS article, not 2023.

### Why it is worth adding

Its taxonomy splits **factuality** hallucination from **faithfulness** hallucination.
The thesis measures faithfulness — groundedness against retrieved chunks — and explicitly
does *not* measure factuality against the world. That distinction is currently made in
prose in §1.5 without a source. Huang et al. names it.

This is also the single best citation for "the hallucination literature" as a body in a
2024+-compliant form: an ACM TOIS survey published 2025.

### Role
**Support** and **framing**. Recommended addition to Chapter 1 §1.5.

---

## 3.4 Siren's Song — now a *Computational Linguistics* article

**Revised 2026-10-16.** The author was right on both counts: this is published, and the
published author list differs from the arXiv one.

| Field | Value |
|---|---|
| Title | Siren's Song in the AI Ocean: A Survey on Hallucination in Large Language Models |
| Authors (**published, 15**) | Yue Zhang; Yafu Li; Leyang Cui; Deng Cai; Lemao Liu; Tingchen Fu; Xinting Huang; Enbo Zhao; Yu Zhang; Yulong Chen; Longyue Wang; Anh Tuan Luu; Wei Bi; Freda Shi; Shuming Shi |
| Venue | ***Computational Linguistics* 51(4), pp. 1373–1418** |
| DOI | **`10.1162/COLI.a.16`** |
| Publisher | MIT Press |
| Date | **2025-12-01** |
| Status | **PUBLISHED**, peer-reviewed |
| arXiv | 2309.01219 — 16 authors, comment "work in progress" |
| Provenance | Crossref, fetched 2026-10-16 — DOI supplied by the author |

### ⚠ Author-list discrepancy — confirmed

**`Chen Xu` appears in the arXiv version and not in the published one.** Verified by
comparing the two records directly: arXiv 16 authors, Crossref 15, with `chen xu` the only
difference. **Cite the 15-author published list.**

This was caught by the author, not by my pipeline, which compared titles between versions
but not author lists. That check now exists (`author_check.py`) and was run across all 12
paired records; this is the only real discrepancy in the set. One benign formatting note it
did surface: Crossref renders FActScore's author as "Pang Koh", dropping the middle name —
use **"Pang Wei Koh"**.

⚠ Also: the Crossref title field carries a **mermaid emoji** (🧜) before "Siren's". Strip
it; it is decoration in the journal's title styling, not part of the title.

### ⚠ Correction to my earlier recommendation

The previous version of this file said to "prefer Huang et al. (§3.3, peer-reviewed TOIS)
for any load-bearing taxonomy claim" because this paper was an unreviewed work in progress.
**That reasoning is void.** *Computational Linguistics* is a top-tier venue for an NLP
survey — arguably stronger than ACM TOIS for this subject. Both are now peer-reviewed
journal articles and either can carry a load-bearing claim.

Its three categories — input-conflicting, context-conflicting, fact-conflicting — are now
citable with confidence, and **context-conflicting** is the one that maps to RAG
hallucination.

### The refusal passage — a find that matters beyond this category

The author identified this passage in the paper:

> "The Moss project (Sun et al. 2023b) open-sourced their SFT data, which includes such
> honest samples. Llama Team (2024) and Wan et al. (2024) **teach the model to refuse to
> answer by incorporating refusal responses into the SFT data.** We observed that models
> tuned with them could learn to refuse to answer specific questions, therefore helping
> reduce hallucinations."

**This is the contrast §1.5 has been missing.** The scope statement asserts:

> "The system does not reduce hallucination at generation time. The underlying language
> model hallucinates at the same rate with or without the proposed layer."

That boundary is currently drawn without naming what the alternative *is*. This passage
names it precisely: the established way to make a model refuse is to **train** it to,
by putting refusal responses in the supervised fine-tuning data. That reduces hallucination
at generation time, and it requires access to the model and its training pipeline.

So it does three jobs:

| Job | Where |
|---|---|
| names the generation-time alternative, so the scope boundary is a contrast rather than an assertion | §1.5 |
| **strengthens Contribution 1** — refusal via SFT requires retraining; refusal via post-hoc verification requires three strings and no model access | Contribution 1 |
| distinguishes REFUSE from learned refusal — a different mechanism family from selective prediction | Objective 3 |

Draft sentence:

> Refusal has been approached as a training objective, with refusal responses incorporated
> into supervised fine-tuning data so that models learn to decline specific questions
> (Zhang et al., 2025, and the work surveyed therein). Such approaches reduce hallucination
> at the point of generation and require access to the model and its training data. The
> mechanism proposed here instead determines refusal after generation, from verification of
> the generated answer against retrieved evidence, and therefore applies to a deployed
> model that cannot be retrained.

⚠ **Sun et al. (2023b), Llama Team (2024) and Wan et al. (2024) are cited second-hand**
through this survey. If any of those claims becomes load-bearing, resolve the primaries.
They are **not currently in `citations.md`** — logged in `unverified.md`.

⚠ Also cross-referenced from `07-selective-prediction.md`: SFT-learned refusal is a third
family alongside selective prediction and evidence-grounded abstention, and §7 does not
currently mention it.

## 3.5 RAGTruth — the RAG-specific corpus

| Field | Value |
|---|---|
| Title | RAGTruth: A Hallucination Corpus for Developing Trustworthy Retrieval-Augmented Language Models |
| Authors | Cheng Niu; Yuanhao Wu; Juno Zhu; Siliang Xu; KaShun Shum; + more |
| Venue | Proceedings of ACL 2024 (Volume 1: Long Papers), **pp. 10862–10878** |
| DOI | `10.18653/v1/2024.acl-long.585` |
| Status | **PUBLISHED**, peer-reviewed |
| Provenance | Crossref, fetched 2026-10-13 |
| Access | metadata verified |

**Satisfies the 2024+ rule** and is the benchmark RT4CHART evaluates on. Relevant for two
reasons: it is the standard RAG hallucination corpus, and RT4CHART's re-annotation of it
found "1.68× more hallucination cases than the original labels", which is a useful caution
about benchmark label quality — directly relevant to this thesis's own labelling defence.

### Role
**Positioning.** Shows the thesis is aware of the standard RAG corpus and explains why a
manufacturing-specific benchmark is used instead.

---

## 3.6 Also verified, lower priority

| Paper | arXiv | Status | Note |
|---|---|---|---|
| The HalluRAG Dataset: Detecting Closed-Domain Hallucinations in RAG Applications Using an LLM's Internal States | 2412.17056 | ⚠ **venue undetermined** — an OpenReview record exists at `openreview.net/pdf?id=pO0s74aF3R`, so it was submitted somewhere. OpenReview returns HTTP 403 from this machine (datacenter IP), so **the venue and decision could not be checked**. Open the forum page in a browser to settle it | internal-states approach — requires access to the model's hidden states, so it **reinforces Contribution 1**: a contrast that cannot be retrofitted to a deployed system |
| Mitigating Hallucination in LLMs: A Capability-Oriented Survey on RAG, Reasoning, and Agentic Systems | 2510.24476 | **SUBMITTED, not published** — the manuscript states it is submitted to ACM (per the author). Do not cite as published; treat as a preprint under review | recent survey; 2024+ compliant |

---

## Summary for Chapter 2

This area needs the least work. Three actions:

1. Add **Huang et al. (2025, TOIS)** for the factuality-vs-faithfulness distinction §1.5
   already relies on implicitly.
2. State the Maynez et al. **adaptation** from summarisation source to retrieved chunks
   explicitly rather than silently.
3. Cite **RAGTruth** once, to show awareness of the standard RAG corpus and justify the
   manufacturing benchmark choice.

4. **Use the refusal passage in §3.4** to give §1.5's generation-time boundary a named
   contrast, and to strengthen Contribution 1.

Keep out: the four-types framing. The earlier caution against using Zhang et al. for
load-bearing claims **no longer applies** — it is a published *Computational Linguistics*
article.
