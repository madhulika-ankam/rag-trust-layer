# Category 10 — Trust Calibration & Over-Reliance

**Supports:** §1.3 (Motivation and Significance), §1.5 (the reliability-vs-trust scope
boundary), the "rely appropriately" wording, Contribution 5
**Prior state:** the conceptual spine of Chapter 1 rested on **ref [7] alone** —
`2604.09174`, now confirmed as an **unreviewed preprint with no DOI**. The chapter
attributes "trust calibration" to "the human-AI interaction literature" while citing a
RAG hallucination-tracing preprint. The actual canon was entirely absent.

**This was the most review-vulnerable point in the thesis.** It is now fixable with one
canonical citation and two recent surveys.

**Domain ladder:** this construct does not exist in the manufacturing literature as
theory — manufacturing papers *apply* it. Searched manufacturing, then general human-AI
interaction, where the foundational work lives. Pre-2024 for the origin paper by
necessity; the two surveys are 2023 and 2024.

---

## 10.1 Lee & See (2004) — the origin of the term

| Field | Value |
|---|---|
| Title | Trust in Automation: Designing for Appropriate Reliance |
| Authors | J. D. Lee; K. A. See |
| Venue | *Human Factors: The Journal of the Human Factors and Ergonomics Society* **46(1), pp. 50–80** |
| DOI | `10.1518/hfes.46.1.50_30392` |
| Publisher | Oxford University Press (per Crossref; the journal is SAGE/HFES — the Crossref publisher field reflects a transfer) |
| Date | 2004-01-01 |
| Status | **PUBLISHED**, peer-reviewed. The canonical reference for calibrated trust |
| Provenance | Crossref API, fetched 2026-10-13 |
| Access | `[search snippet]` — metadata verified, full text not yet read |

### Why this citation is mandatory

The thesis uses the phrase "trust calibration" and the argument "rely appropriately
rather than rely more". **Lee & See is where that framing originates**, and its subtitle
is literally "Designing for Appropriate Reliance". Citing a 2026 RAG preprint for this
construct instead of Lee & See is the kind of thing a committee member in a
human-factors-adjacent field notices immediately — and Dr. Morkos's MODEL Lab sits in
engineering design, where this literature is standard.

### Concepts it supplies, that the thesis already uses implicitly

Reported by secondary sources `[search snippet]` — **verify against the paper before
quoting**:

- Trust defined as "the attitude that an agent will help achieve an individual's goals
  in a situation characterized by uncertainty and vulnerability"
- **Calibration** — how closely trust matches actual capability
- **Resolution** — how well trust tracks *changes* in capability
- Miscalibration in two directions: **overtrust** and **distrust** (under-trust)

The calibration/resolution distinction is worth adopting deliberately. The thesis's
per-answer trust score is an attempt to improve *resolution* — making the operator's trust
vary with the reliability of each individual answer — not merely to raise or lower overall
trust. That is a sharper statement of the contribution than "supports calibrated trust",
and it comes free with the citation.

### What to read
- The abstract and the conceptual model section — the calibration / resolution definitions
- The appropriate-reliance framing
- **Skip:** the full review of pre-2004 automation studies

### Role
**Support**, and a **framing** citation. Replaces ref [7] as the source for trust calibration.

⚠ **Full text not yet obtained.** All concept descriptions above are from secondary
sources. Do not quote the paper until the original is read.

---

## 10.2 Mehrotra et al. (2024) — the recent systematic review

| Field | Value |
|---|---|
| Title | A Systematic Review on Fostering Appropriate Trust in Human-AI Interaction: Trends, Opportunities and Challenges |
| Authors | Siddharth Mehrotra; Chadha Degachi; Oleksandra Vereschak; Catholijn M. Jonker; Myrthe L. Tielman |
| Venue | *ACM Journal on Responsible Computing* **1(4), pp. 1–45** |
| DOI | `10.1145/3696449` |
| Date | 2024-12-31 |
| Status | **PUBLISHED**, peer-reviewed |
| arXiv | 2311.06305 (preprint version, 39 pages) |
| Provenance | Crossref + arXiv API, fetched 2026-10-13 |
| Access | `[search snippet]` |

**Satisfies the 2024+ recency rule** while covering the construct. A 45-page systematic
review in an ACM journal is a strong single citation for "the human-AI interaction
literature" as a body — which is what §1.3 currently claims without support.

Use it where the chapter needs to refer to the literature collectively rather than to one
study. It also supplies the under-reliance / over-reliance framing that §1.3's asymmetry
argument depends on.

---

## 10.3 Wischnewski, Krämer & Müller (2023) — measurement

| Field | Value |
|---|---|
| Title | Measuring and Understanding Trust Calibrations for Automated Systems: A Survey of the State-Of-The-Art and Future Directions |
| Authors | Magdalena Wischnewski; Nicole Krämer; Emmanuel Müller |
| Venue | Proceedings of the 2023 CHI Conference on Human Factors in Computing Systems, ACM, **pp. 1–16** |
| DOI | `10.1145/3544548.3581197` |
| Date | 2023-04-19 |
| Status | **PUBLISHED**, peer-reviewed (CHI) |
| Provenance | Crossref API, fetched 2026-10-13 |
| Access | `[search snippet]` |

### Why this one specifically

§1.5 states that "Human trust and adoption are not directly measured" and defers a
deployment study to future work. **This paper is how that future work would be
designed** — it surveys how trust calibration is actually measured.

Citing it converts the scope limitation from an admission into an informed decision: the
thesis knows what measuring trust calibration requires, and states that it is out of
scope. That is a materially stronger position in a viva than leaving the limitation bare.

---

## 10.4 Keep ref [7], but demote it

`2604.09174` — Elchafei, Swain, Masoudian & Schedl (2026), *Facet-Level Tracing of
Evidence Uncertainty and Hallucination in RAG*. Unreviewed preprint, no DOI.

It should **not** carry the definition of trust calibration. It *is* appropriate for the
narrower empirical claim it actually supports — that RAG models override retrieved
evidence, and that users may therefore over-rely on the assumption that retrieval
guarantees faithfulness. That is its own finding and worth keeping.

Recommended split in §1.3:

| Claim | Cite |
|---|---|
| trust calibration as a construct | **Lee & See (2004)**, with Mehrotra et al. (2024) for the literature as a body |
| "rely appropriately, not rely more" | **Lee & See (2004)** — its subtitle |
| measuring calibration is a study design in itself | **Wischnewski et al. (2023)** |
| models override retrieved evidence; users over-rely | ref [7] `2604.09174` — but flag it as a preprint |

---

## Still missing from this category

| Needed for | Candidate | Status |
|---|---|---|
| over-reliance on AI advice, empirically | Bansal et al.; Buçinca et al.; Vasconcelos et al. | **not yet searched** |
| automation use/misuse/disuse | Parasuraman & Riley (1997) | **not yet searched** |
| explanations and reliance | Zhang, Liao & Bellamy | **not yet searched** |

These are the empirical over-reliance studies. They matter for §1.3's asymmetry argument
(the operator who over-relies may follow an unsafe procedure), which is currently
supported by reasoning rather than by evidence. Recommended for the next pass.
