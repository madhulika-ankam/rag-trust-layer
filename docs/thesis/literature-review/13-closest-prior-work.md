# Category 13 — Closest Prior Work (Competitor Triage)

**Status:** Phase 0 complete, 2026-10-13.
**Why this category ran first:** these papers determine how every other category is framed.

All metadata below was resolved against the arXiv API during this session
(`https://export.arxiv.org/api/query`). No field is reproduced from memory.

---

## 13.1 RT4CHART — the previously un-triaged competitor

| Field | Value |
|---|---|
| Title | Retromorphic Testing with Hierarchical Verification for Hallucination Detection in RAG |
| Authors | Boxi Yu; Yuzhong Zhang; Liting Lin; Lionel Briand; Emir Muñoz |
| arXiv | 2603.27752 (v2) |
| Submitted | 2026-03-29 · v2 2026-07-20 |
| Category | cs.CL |
| DOI / venue | **none** — unreviewed preprint |
| Access | full text read (arXiv HTML v2) |
| Provenance | `https://arxiv.org/html/2603.27752v2`, fetched 2026-10-13 |

**Note:** the bibliography contains `Anonymous (2026) A toolkit for ASE 2026 research
track paper rt4chart` — i.e. it is under submission to ASE 2026. Treat as
*preprint under review*, not as published.

### Why it matters

This paper was surfaced once in the thesis conversation (line 9346) and then dropped
without triage. It is a closer architectural match to Contributions 2 and 5 than
Explain-RAG is.

What it does, from the abstract `[full text]`:

> "RT4CHART decomposes an answer into independently verifiable claims, performs
> hierarchical local-to-global verification against the retrieved context, and assigns
> each claim one of three labels: entailed, contradicted, or baseless. It further maps
> these claim-level decisions back to specific answer spans and returns explicit
> context-side evidence, enabling fine-grained auditing rather than opaque scoring."

### What this costs the thesis

**Contribution 2 (claim-level verification) is no longer distinctive on its own.**
RT4CHART decomposes the *generated answer* — not the query — and verifies each claim
against the *retrieved context*. That is the same decomposition target and the same
evidence source as this thesis. The answer-vs-query distinction that differentiates
this work from `2605.21949` does **not** differentiate it from RT4CHART.

**Contribution 5 (per-claim citation trail) is substantially overlapped.** RT4CHART
maps claims back to answer spans *and* returns context-side evidence. Of the three
transparency layers, only the natural-language explanation remains clearly unaddressed.

**The "answer-level detectors" criticism is now shared, not owned.** RT4CHART opens
with the same critique this thesis makes of Explain-RAG `[full text]`:

> "many existing detectors return holistic answer-level scores, while others target
> open-domain factuality or fail to provide evidence-grounded diagnostics."

### What survives — and it is the decisive finding

**RT4CHART never withholds anything. It is a detector, not a gate.**

Term counts over the full text:

```
abstain      0     delivery     0     middleware   0
abstention   0     deliver      0     plug         0
withhold     0     gating       0     post-hoc     0
refuse       0     downstream   0
```

All five occurrences of "decision" refer to *claim-label* decisions, never delivery
decisions. The paper's own stated purpose is auditing `[full text]`:

> "For auditing purposes, however, it is not enough to flag an LLM answer as
> problematic. A useful detector must also identify which part of the answer is
> unsupported and ground that judgment in explicit context evidence."

It states that detection should happen "before they reach end users" but implements
no mechanism to stop them:

> "A single unsupported claim in a deployed system can erode user trust and lead to
> flawed decisions. Detecting such unfaithful outputs before they reach end users is
> therefore essential."

**Three further differentiators, all verified from the full text:**

1. **Mechanism — it is an LLM judge, not NLI.** Default judge model is **GPT-4o mini**
   (§4.2). Thresholds for its baselines come from Vectara's recommended 0.5. This
   thesis's NLI + rule-based cascade runs locally with no per-query API cost, which is
   a deployment argument RT4CHART cannot make.
2. **No rule-based mechanisms.** No entity matching, no numerical comparison, no
   negation handling. Contribution 3 is untouched.
3. **Domain.** Evaluated on RAGTruth++ (408 samples) and RAGTruth-Enhance (2,675) —
   general domain. No manufacturing, no safety-critical regulatory text.

### Verdict

The post-hoc middleware headline **survives, but it is no longer sufficient on its
own**. RT4CHART is also post-hoc over a completed answer.

The defensible remaining position is the **conjunction**, which neither competitor has:

```
2605.21949  four-way decision  +  claim decomposition  −  post-hoc (decomposes QUERY,
            (Claim-Selective)                              acts before response formed)

2603.27752  post-hoc  +  answer-level claim decomposition  −  any delivery decision
            (RT4CHART)    + span/evidence attribution        (detector only)

This thesis   post-hoc  +  answer-level claim decomposition  +  verification-gated
                           delivery  +  rule-based cascade  +  manufacturing safety
```

**Required wording changes:**

- Contribution 2 must cite RT4CHART and stop resting on claim-level granularity as the
  distinction. The distinction is that claim labels *govern delivery*.
- Contribution 5 must acknowledge span-level attribution exists, and narrow its claim
  to the three-audience layering and the natural-language explanation.
- Any sentence implying this thesis is first to do post-hoc claim-level verification of
  a generated answer must go.

---

## 13.2 Claim-Selective Certification — two open questions now closed

| Field | Value |
|---|---|
| Title | **Claim-Selective Certification for High-Risk Medical Retrieval-Augmented Generation** |
| Authors | Shao Kan (single author) |
| arXiv | 2605.21949 (v1 only) |
| Submitted | 2026-05-21 — still v1 as of 2026-10-13 |
| DOI / venue | **none** — unreviewed preprint |
| Comment | 22 pages, 7 figures, 11 tables |
| Provenance | arXiv API, fetched 2026-10-13 |

Two project questions resolved:

1. **The title ambiguity is settled.** The project carried two variants; the arXiv
   record uses the long form — "…High-Risk Medical **Retrieval-Augmented Generation**",
   not "…Medical RAG". Use the long form.
2. **Peer-review status: unreviewed preprint.** Recorded as unknown in the project.
   Still v1 five months after submission, no DOI, no journal reference.

This is good news for positioning. "Concurrent preprint work" is accurate and the
framing in `chapter-1-contributions-revision.md` already uses it correctly.

---

## 13.3 MedTrust-RAG — triaged, and it *helps*

| Field | Value |
|---|---|
| Title | MedTrust-RAG: Evidence Verification and Trust Alignment for Biomedical Question Answering |
| Authors | Yingpeng Ning; Yuanyuan Sun; Ling Luo; Yanhua Wang; Yuchen Pan; Hongfei Lin |
| arXiv | 2510.14400 (v2) |
| Submitted | 2025-10-16 · v2 2025-10-18 |
| Venue | **Accepted as a short paper at IEEE BIBM 2025** (the arXiv comment reads "BlBM2025" — an OCR/typo for BIBM; confirm the exact venue string before citing) |
| Access | abstract only |
| Provenance | arXiv API, fetched 2026-10-13 |

From the abstract `[abstract only]`, its three mechanisms are:

> "First, it enforces citation-aware reasoning by requiring all generated content to be
> explicitly grounded in retrieved medical documents, with structured Negative Knowledge
> Assertions used when evidence is insufficient. Second, it employs an iterative
> retrieval-verification process, where a verification agent assesses evidence adequacy
> and refines queries through Medical Gap Analysis until reliable information is
> obtained. Third, it integrates the MedTrust-Align Module (MTAM) … leveraging Direct
> Preference Optimization to reinforce citation-grounded reasoning while penalizing
> hallucination-prone response patterns."

**This is a *supporting* citation, not a threat.** Every one of its three mechanisms
requires deep access to the host pipeline: it constrains generation prompting, it loops
retrieval, and it fine-tunes the model with DPO. It is the clearest published example
of the alternative Contribution 1 is distinguished *from* — verification that cannot be
retrofitted to a deployed system.

Use it in Contribution 1 and in Chapter 2 as evidence that the pipeline-modifying
approach is the norm. It is also **peer-reviewed**, unlike the other two, which makes
it the strongest citation of the three for that argument.

Secondary note: "Negative Knowledge Assertions … when evidence is insufficient" is an
abstention-adjacent mechanism — relevant to category 7 and to the unbuilt Module 2.

---

## 13.4 Harvest — verified citations from RT4CHART's bibliography

RT4CHART's reference list supplies full venues and page numbers for papers this thesis
needs and currently lacks. **Provenance: RT4CHART bibliography (secondary source).**
Each must be confirmed against the ACL Anthology before submission; they are listed here
as high-confidence leads, not as verified primaries.

| Paper | Citation as given | Fills category |
|---|---|---|
| SNLI | Bowman, Angeli, Potts & Manning (2015), EMNLP 2015, pp. 632–642 | 5 — never cited before |
| SummaC | Laban, Schnabel, Bennett & Hearst (2022), *TACL* 10, pp. 163–177 | 5, 12 |
| FActScore | Min, Krishna, Lyu, Lewis, Yih, Koh, Iyyer, Zettlemoyer & Hajishirzi (2023), EMNLP 2023, pp. 12076–12100 | 4 — **uncited claim** |
| VeriScore | Song, Kim & Iyyer (2024), Findings of EMNLP 2024, pp. 9447–9474 | 4 |
| SAFE / long-form factuality | Wei, Yang, Song, Lu, Hu, Tran, Peng, Liu, Huang, Du & Le (2024), NeurIPS 2024 | 4 |
| MiniCheck | Tang, Laban & Durrett (2024), EMNLP 2024, pp. 8818–8847 | 5 |
| AlignScore | Zha, Yang, Li & Hu (2023), ACL 2023, pp. 11328–11348 | 5 |
| ALCE / citations | Gao, Yen, Yu & Chen (2023), EMNLP 2023, pp. 6465–6488 | 9 — **uncited claim** |
| RAGTruth | Niu, Wu, Zhu, Xu, Shum, Zhong, Song & Zhang (2024), ACL 2024, pp. 10862–10878 | 12 |
| SelfCheckGPT | Manakul, Liusie & Gales (2023), EMNLP 2023 | 3, 11 |
| LettuceDetect | Kovács & Recski (2025), arXiv 2502.17125 | 5 |
| Lynx | Ravi, Mielczarek, Kannappan, Kiela & Qian (2024), arXiv 2407.08488 | 5 |

### ⚠ Correction to an existing Chapter 1 reference

Reference [8] in `chapter-1-introduction.md` gives Ji et al. as
`ACM Computing Surveys, 55(12), 1–38`. RT4CHART's bibliography gives
`ACM Computing Surveys 55(12), pp. 248:1–248:38` — i.e. **article number 248**.
ACM paginates by article. Confirm against the ACM Digital Library and correct.

---

## Open items carried forward

- `2510.14400` venue string: the arXiv comment reads "BlBM2025". Confirm it is IEEE BIBM
  2025 and get the proceedings citation.
- RT4CHART's ASE 2026 submission status: check whether it is accepted before submission,
  since that changes it from preprint to published prior art.
- The twelve harvested citations above need primary confirmation against the ACL
  Anthology / ACM DL.
- Still unexamined from the "surfaced but never discussed" list: RAGalyst `2511.04502`,
  PlainQAFact `2503.08890`.
