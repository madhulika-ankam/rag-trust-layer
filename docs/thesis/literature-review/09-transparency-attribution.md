# Category 9 — Transparency, Attribution & Explainability

**Supports:** Contribution 5 (the three-layer transparency report), Module 7
(`reporter.py`), the per-claim citation trail
**Prior state:** **zero citations.** The claim that a machine-readable score, a per-claim
citation trail and a natural-language explanation "address the distinct needs of automated
auditing, safety engineering review, and shop-floor use respectively" had no source at all.

⚠ **Read `13-closest-prior-work.md` first.** RT4CHART already maps claim-level decisions
to answer spans and returns explicit context-side evidence. Contribution 5 must narrow to
the three-audience layering and the natural-language explanation.

**Domain ladder:** no manufacturing-domain attribution work. General NLP supplies a clean
lineage, with the foundational attribution framework pre-2024 by necessity.

---

## 9.1 Rashkin et al. — the attribution framework (AIS)

| Field | Value |
|---|---|
| Title | Measuring Attribution in Natural Language Generation Models |
| Authors | Hannah Rashkin; Vitaly Nikolaev; Matthew Lamm; Lora Aroyo; Michael Collins; Dipanjan Das; Slav Petrov |
| arXiv | 2112.12870 (2021-12-23) |
| Status | PREPRINT record — no DOI. Widely cited; commonly published as *Computational Linguistics* (2023). **Confirm the journal version** |
| Provenance | arXiv API, fetched 2026-10-13 |
| Access | metadata verified |

The **Attributable to Identified Sources (AIS)** framework — the standard formalisation of
what it means for a generated statement to be attributable to a specific source.

**This is the missing conceptual foundation for the citation trail.** Contribution 5's
middle layer is an AIS-style attribution claim: each statement is traced to the document
supporting it. Citing AIS gives the layer a name and a definition rather than presenting it
as an implementation feature.

---

## 9.2 Gao et al. — generating text with citations (ALCE)

| Field | Value |
|---|---|
| Title | Enabling Large Language Models to Generate Text with Citations |
| Authors | Tianyu Gao; Howard Yen; Jiatong Yu; Danqi Chen |
| Venue | Proceedings of EMNLP 2023, **pp. 6465–6488** |
| DOI | `10.18653/v1/2023.emnlp-main.398` |
| Status | **PUBLISHED**, peer-reviewed |
| Provenance | Crossref, fetched 2026-10-13 |

The ALCE benchmark for citation generation and evaluation. The important **contrast** for
this thesis: ALCE has the *generator* produce citations as it writes. This thesis derives
attribution *post-hoc*, from verification, without the generator's cooperation.

That is the same post-hoc-versus-integrated distinction that carries Contribution 1 — so
this citation does double duty: it grounds the attribution layer and reinforces the
headline pluggability argument.

---

## 9.3 Liu et al. — attribution fails in practice

| Field | Value |
|---|---|
| Title | Evaluating Verifiability in Generative Search Engines |
| Authors | Nelson F. Liu; Tianyi Zhang; Percy Liang |
| Venue | Findings of EMNLP 2023 (per arXiv comment) |
| arXiv | 2304.09848 — 25 pages, 12 figures |
| Status | Findings of EMNLP 2023 — **confirm the Anthology citation** |
| Provenance | arXiv API, fetched 2026-10-13 |

Evaluates whether deployed generative search engines' citations actually support their
statements. This is the **motivation** citation for why verified attribution matters: a
citation that does not support its claim is worse than no citation, because it manufactures
unwarranted confidence.

That is precisely the §1.2 argument — fluent confident prose regardless of grounding —
applied to attribution specifically, with empirical backing.

---

## 9.4 Explainability for different audiences

| Field | Value |
|---|---|
| Title | Explainability for Large Language Models: A Survey |
| Authors | in `citations.md` (resolved via arXiv API) |
| arXiv | 2309.01029 |
| Status | PREPRINT — no DOI |
| Access | metadata verified |

Already in the project's reading list (Group 4, attributed to Zhao et al., 2023). Use it as
the single survey citation for the explainability framing.

⚠ **It does not support the three-audience claim.** Contribution 5 asserts that the three
layers serve automated auditing, safety engineering review and shop-floor use respectively.
**No citation found for that specific stakeholder decomposition.** Two honest options:

1. **Soften it.** State the three layers and what each affords, without claiming they map
   onto three validated audience needs.
2. **Find support.** The stakeholder-specific XAI literature (different explanations for
   different roles) likely supports it, but it was **not searched** in this pass. Recorded
   in `unverified.md` §D.

Recommend option 1 unless the claim is load-bearing for the viva.

---

## Summary for Chapter 2

> Attribution of generated statements to identified sources has been formalised as the AIS
> framework (Rashkin et al., 2021), and benchmarked for generator-produced citations by
> Gao et al. (2023). Liu et al. (2023) show that citations produced by deployed generative
> search engines frequently fail to support the statements they accompany, which makes
> unverified attribution a source of unwarranted confidence rather than a remedy for it.
> The transparency report proposed here differs from citation-generation approaches in
> deriving attribution from verification after generation: each claim's citation is the
> evidence chunk against which it was actually checked, rather than a reference the
> generator was prompted to emit.

That last sentence is the real contribution of this layer, and it survives RT4CHART —
which returns evidence but does not gate delivery on it.
