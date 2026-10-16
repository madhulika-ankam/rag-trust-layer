# Category 1 — Manufacturing & Industrial RAG

**Supports:** §1.1, §1.2, Objective 4, Contribution 6, Chapter 2 area 3
**Revised 2026-10-15** with DOIs supplied by the author, all verified against Crossref.

**Status transformed.** This category was five preprints out of seven. It is now
**eleven peer-reviewed journal or conference papers out of twelve** — including the
benchmark paper itself, which has been published since the earlier pass.

**Domain ladder:** this *is* the manufacturing tier, and it is stronger than the first
pass suggested. See §1.8 for what that means for the gap claim — it now needs re-testing
rather than restating.

---

## 1.1 Singh et al. — the benchmark, now a journal article

| Field | Value |
|---|---|
| Title | A Multimodal Manufacturing Safety Chatbot: Knowledge Base Design, Benchmark Development, and Evaluation of Multiple RAG Approaches |
| Authors | Ryan Singh; Austin Hamilton; Amanda White; Michael Wise; Ibrahim Yousif; Arthur Carvalho; Zhe Shan; Reza Abrisham Baf; Mohammad Mayyas; Lora A. Cavuoto; Fadel M. Megahed (11) |
| Venue | ***Manufacturing Letters* 49, pp. 30–41** |
| DOI | **`10.1016/j.mfglet.2026.07.012`** |
| Publisher | Elsevier BV |
| Date | **2026-10** |
| Status | **PUBLISHED**, peer-reviewed journal article |
| arXiv | 2511.11847 (preprint, v2 2026-02-10) |
| Provenance | Crossref, fetched 2026-10-15 — DOI supplied by the author |

### Why this matters more than a formatting fix

§1.2 pivots on "A system that is correct 86.66% of the time and silent about which 86.66%."
On the earlier pass that figure rested on an **unreviewed preprint**, which was a real
weakness in the chapter's central argument. It is now a peer-reviewed Elsevier journal
article. **Cite the journal version**, and the acknowledging clause I suggested earlier is
no longer needed.

Refs [1] and [3] in Chapter 1 are still the same paper cited twice — merge them, keep the
full eleven-author list, and use the *Manufacturing Letters* citation.

### Two things to check in the published version

⚠ **The 153-vs-161 question count.** The preprint reports 153 (60 UR5e + 51 Haas + 42
Bridgeport); the file Megahed supplied has 161 rows. The journal version may have changed
the count, resolved it, or preserved it. **Check this against the published paper** — if
the published count differs again, that changes what you write in the methodology.

⚠ **The trust-calibration future-work statement.** Your gap argument in §1.3 relies on
Singh et al. naming trust calibration, over-reliance and under-reliance as future work from
their own deployment. Journal revisions often rewrite future-work sections. **Verify it
survives in the published version** before the gap argument leans on it.

---

## 1.2 Kernan Freire et al. — the title question, answered

| Field | Value |
|---|---|
| Published title | Knowledge sharing in manufacturing using LLM-powered tools: user study and model benchmarking |
| Authors | Samuel Kernan Freire; Chaofan Wang; Mina Foosherian; Stefan Wellsandt; Santiago Ruiz-Arenas; Evangelos Niforatos (6) |
| Venue | *Frontiers in Artificial Intelligence* **7**, article **1293084** |
| DOI | `10.3389/frai.2024.1293084` |
| Date | 2024-03-27 |
| Status | **PUBLISHED**, peer-reviewed |
| arXiv | 2401.05200 — different title, comment still reads "Under review" |

**You are right that the content matches, and that was never the concern.** The issue is
narrower than it looked: the two versions carry **different title strings**, and ref [4]
currently pairs the *arXiv* title with the *Frontiers* venue. That is a citation that
describes no actual object — a reader following it to Frontiers finds a differently-titled
article.

It is purely a reference-list decision, not a content problem:

| Cite as | Title to use |
|---|---|
| **Frontiers (recommended)** | "Knowledge sharing in manufacturing using LLM-powered tools: user study and model benchmarking", *Frontiers in Artificial Intelligence* 7:1293084, DOI `10.3389/frai.2024.1293084` |
| arXiv preprint | "Knowledge Sharing in Manufacturing using Large Language Models: User Evaluation and Model Benchmarking", arXiv:2401.05200 |

Use the Frontiers version — it is peer-reviewed and it is what you quote from.

⚠ Still outstanding regardless of which title you choose: the **"you risk safety"**
quotation in §1.2 must be verified word-for-word against the published version, and the
broken `(cite index="53-1">` markup tag around it cleaned up.

---

## 1.3 Brehme et al. — you are right, it is industrial but not manufacturing

| Field | Value |
|---|---|
| Title | Retrieval-Augmented Generation in Industry: An Interview Study on Use Cases, Requirements, Challenges, and Evaluation |
| Authors | Lorenz Brehme; Benedikt Dornauer; Thomas Ströhle; Maximilian Ehrhart; Ruth Breu |
| Venue | Proceedings of the 17th International Joint Conference on Knowledge Discovery, Knowledge Engineering and Knowledge Management (**KDIR / IC3K 2025**), **pp. 110–122** |
| DOI | `10.5220/0013739500004000` |
| Publisher | SCITEPRESS |
| Status | **PUBLISHED**, peer-reviewed conference paper |

**Your reading is correct and it changes how this should be cited.** The study is of RAG
deployment across *industrial organisations* generally — not manufacturing, and not safety.
The category heading is "Manufacturing **& Industrial** RAG", so it belongs here, but the
distinction matters for what it can support:

| Can support | Cannot support |
|---|---|
| that verifiability is a barrier to RAG adoption **in industry** | anything specific to manufacturing |
| that industrial evaluation is predominantly manual expert review | anything about safety-critical procedural text |
| the generality of the problem beyond one factory | the manufacturing-specific gap claim |

So keep it in §1.2 where it generalises the verifiability barrier beyond Kernan Freire's
single factory — that is exactly what a cross-industry interview study is good for. Do not
let it carry a manufacturing claim. **If you would rather not have it in this category at
all, it would sit equally well in category 2** as high-stakes-deployment evidence; say the
word and I will move it.

⚠ Unverified: the reported finding that industrial evaluations are "predominantly performed
manually by human experts" comes from a search snippet, not the paper. Check it.

---

## 1.4 Freeman et al. — the concern, explained plainly

| Field | Value |
|---|---|
| Title | Toward Epistemic Stability: Engineering Consistent Procedures for Industrial LLM Hallucination Reduction |
| Authors | Brian Freeman; Adam Kicklighter; Matt Erdman; Zach Gordon |
| Venue | *Computer and Information Science* **19(2), p. 1** |
| Publisher | **Canadian Center of Science and Education (CCSE)** |
| DOI | `10.5539/cis.v19n2p1` |
| Date | 2026-05-26 |
| Status | PUBLISHED — the record is real and resolves correctly |
| arXiv | 2603.10047 (50 pages, 5 tables, 7 figures) |

**You are right that it is there, and the paper is not the problem.** My concern was about
the *publisher*, and I should have stated it concretely instead of just flagging it. Here
it is, with what I could and could not establish:

**What I could establish.** CCSE appeared on Jeffrey Beall's list of "potential, possible,
or probable predatory scholarly open-access publishers", and still appears in the
maintained archive of that list. CCSE threatened legal action over the listing in 2013.
The archive's own guidance is that it should be used as a **screening tool, not a verdict**.

**What I could not establish.** Whether any CCSE title is currently indexed in Scopus or
Web of Science. My sources were a 2013 news report, a 2016 blog post and a list archive —
none is a current formal finding, and none addresses *Computer and Information Science*
specifically. **You can settle this in two minutes**: search the Web of Science Master
Journal List and the Scopus Source List for the journal title. If it is indexed, most of my
concern evaporates.

**Why it matters for your thesis, concretely.** This reference carries the requirement that
industrial outputs be "correct for the specific instance and **auditable after the fact**"
— which is effectively your design requirement, so it is load-bearing. The risk is not that
the paper is wrong; it is that a committee member who checks the venue and finds it
unindexed may discount the requirement, and the requirement is doing real work in your
argument.

**Recommendation unchanged, but now with a reason you can weigh.** Keep the citation, and
pair that specific claim with a second source from a venue nobody will question — Brehme
et al. (§1.3, KDIR) covers adjacent ground, and the new *IJPR* and *Sensors* papers in
§1.6 may cover it better. Then the argument survives regardless of how the venue is judged.

---

## 1.5 ManuRAG — now published, and the authors differ from the preprint

| Field | Value |
|---|---|
| Title | ManuRAG: multi-modal retrieval augmented generation for manufacturing question answering |
| Authors | **Yunqing Li; Zihan Dong; Farhad Ameri; Jianbang Zhang** (4) |
| Venue | ***Journal of Intelligent Manufacturing*** |
| DOI | **`10.1007/s10845-026-02800-y`** |
| Publisher | Springer |
| Date | **2026-03-15** |
| Status | **PUBLISHED**, peer-reviewed journal article |
| arXiv | 2601.15434 — titled "**(Early Version)**" |
| Provenance | Crossref, fetched 2026-10-15 — DOI supplied by the author |

Cite the **journal version**, not the arXiv "Early Version". *Journal of Intelligent
Manufacturing* is a well-regarded venue and this is a manufacturing-specific RAG paper, so
it is a stronger related-work citation than the preprint was.

Your earlier assessment stands on the dataset: 1,515 QA pairs on manufacturing
*principles*, not safety regulations — correctly rejected as an evaluation set. It remains
valuable as related work showing multimodal manufacturing QA is an active published area.

---

## 1.6 The four journal papers — all verified

Supplied by the author and confirmed via Crossref, 2026-10-15. These were the unresolved
leads from the first pass. **All four are peer-reviewed journal articles**, which is what
this category was short of.

### ① Troubleshooting assistant — a second motivation anchor

| Field | Value |
|---|---|
| Title | Can a troubleshooting AI assistant improve task performance in industrial contexts? |
| Authors | Nils Löwhagen; Philippe Schwendener; Torbjørn Netland |
| Venue | *International Journal of Production Research*, **pp. 1–22** |
| DOI | `10.1080/00207543.2025.2527368` |
| Date | 2025-07-09 |
| Status | **PUBLISHED**, peer-reviewed |

**The most valuable of the four.** *IJPR* is a leading production-research journal, and
this is an **empirical study of whether an AI assistant actually improves operator task
performance** in an industrial setting.

Right now §1.2's entire empirical basis is Kernan Freire et al. — one factory study. This
gives you a **second independent study** of operator-facing AI assistance in industry, in a
venue your committee will recognise immediately. Whatever it concludes, it strengthens the
motivation: if performance improves, that raises the stakes of unverified answers; if it
does not, that is evidence the barrier is not capability.

**Read this one.** It is the paper most likely to change how §1.2 and §1.3 are written.

### ② Hybrid RAG for smart manufacturing

| Field | Value |
|---|---|
| Title | Empowering LLMs by hybrid retrieval-augmented generation for domain-centric Q&A in smart manufacturing |
| Authors | Yuwei Wan; Zheyuan Chen; Ying Liu; Chong Chen; Michael Packianather |
| Venue | *Advanced Engineering Informatics* **65**, article **103212** |
| DOI | `10.1016/j.aei.2025.103212` |
| Date | 2025-05 |
| Status | **PUBLISHED**, peer-reviewed |

Manufacturing-specific RAG in a strong engineering-informatics journal. Directly comparable
to your baseline pipeline, and the word "hybrid" in the title means its retrieval design
should be checked against yours. **Also check what it reports** — if it reports only
accuracy-style metrics, it is further evidence for the gap in §1.8.

### ③ Knowledge-graph RAG for failure mode and effects analysis

| Field | Value |
|---|---|
| Title | Knowledge graph enhanced retrieval-augmented generation for failure mode and effects analysis |
| Authors | Lukas Bahr; Christoph Wehner; Judith Wewerka; José Bittencourt; **Ute Schmid**; Rüdiger Daub |
| Venue | *Journal of Industrial Information Integration* **45**, article **100807** |
| DOI | `10.1016/j.jii.2025.100807` |
| Date | 2025-05 |
| Status | **PUBLISHED**, peer-reviewed |

**The closest domain match of the four.** FMEA is failure analysis — safety-adjacent
manufacturing reasoning, which is nearer your subject than general manufacturing QA. Note
**Ute Schmid** among the authors, who works in explainable AI; that makes it worth checking
whether the paper makes transparency or explanation claims, in which case it is relevant to
Contribution 5 as well as to this category.

### ④ AI trustworthiness in manufacturing — the resolved placeholder

| Field | Value |
|---|---|
| Title | AI Trustworthiness in Manufacturing: Challenges, Toolkits, and the Path to Industry 5.0 |
| Authors | M. Nadeem Ahangar; Z. A. Farhat; Aparajithan Sivanathan |
| Venue | *Sensors* **25(14)**, article **4357** |
| DOI | `10.3390/s25144357` |
| Publisher | MDPI |
| Date | 2025-07-11 |
| Status | **PUBLISHED**, peer-reviewed |

This resolves the paper your project named as "MDPI *Sensors*, 2025" with no DOI or
volume — it had been sitting in `unverified.md` since the first pass. Use it as the broad
framing citation for why trustworthiness and transparency matter in manufacturing AI, which
is the role your earlier notes assigned it.

---

## 1.7 Also in this category

| Paper | Citation | Status |
|---|---|---|
| **Engineering RAG Systems for Real-World Applications: Design, Development, and Evaluation** | DOI `10.1007/978-3-032-04200-2_10`, **LNCS 16082, pp. 143–158, 2026**, Springer. arXiv `2506.20869` | **PUBLISHED**, peer-reviewed |
| **DesignQA: A Multimodal Benchmark for Evaluating Large Language Models' Understanding of Engineering Documentation** | Anna C. Doris; Daniele Grandi; Ryan Tomich; Md Ferdous Alam; Mohammadmehdi Ataei; Hyunmin Cheong; Faez Ahmed — *Journal of Computing and Information Science in Engineering* **25(2)**, article 021009. DOI **`10.1115/1.4067333`**, ASME, 2025-02 | **PUBLISHED**, peer-reviewed |
| **An Agile Method for Implementing Retrieval Augmented Generation Tools in Industrial SMEs** | Mathieu Bourdin; Anas Neumann; Thomas Paviot; Robert Pellerin; Samir Lamouri — arXiv `2508.21024`, 2025-08-28 | **PREPRINT** — the only one left in this category |

⚠ **DesignQA has two versions with different titles.** The journal article above, and a
DETC 2024 conference paper, "DesignQA: Benchmarking Multimodal Large Language Models on
Questions Grounded in Engineering Documentation", DOI `10.1115/detc2024-139024`, with a
six-author list that omits Ataei. **Cite the JCISE journal version.** Your project had
DesignQA with no citation at all; it now has one, which matters because your prior work
planned to cite it as evidence that document-grounded engineering QA is a recognised and
challenging problem.

---

## 1.8 ⚠ The gap claim now needs re-testing, not restating

This is the consequence of the upgrade, and it cuts both ways.

The first-pass gap statement said the manufacturing literature reports accuracy, cost and
latency without reporting whether individual answers are supported by their retrieved
evidence. **That claim was formed before these four journal papers were in hand.** It may
still hold — but it is no longer safe to assert, because the new papers are exactly the
kind that could falsify it:

| Paper | What to check |
|---|---|
| Bahr et al. (FMEA) | does the knowledge-graph grounding include any verification or confidence step? Does it gate output? |
| Wan et al. (hybrid RAG) | what metrics are reported? Any faithfulness or groundedness measure? |
| Löwhagen et al. (troubleshooting) | does the study measure operator trust or reliance? If so it is close to your §1.3 |
| Ahangar et al. (trustworthiness) | does it propose or survey verification mechanisms, or only discuss trustworthiness as a challenge? |

**Do this before writing the gap paragraph.** The gap is your central positioning claim and
it is now the one part of this category resting on an incomplete survey. Four abstracts is
perhaps an hour's work, and the outcome is either a confirmed gap you can state with
confidence, or an early warning you would much rather have now than in a viva.

If the gap holds, the statement is also **stronger** than before, because it can now be
made against a body of peer-reviewed journal work rather than against preprints:

> Manufacturing and industrial RAG is an established, journal-published area. Singh et al.
> (2026, *Manufacturing Letters*) report a multimodal manufacturing safety chatbot across
> twenty-four configurations; Li et al. (2026, *Journal of Intelligent Manufacturing*)
> address multimodal manufacturing question answering; Wan et al. (2025, *Advanced
> Engineering Informatics*) and Bahr et al. (2025, *Journal of Industrial Information
> Integration*) develop hybrid and knowledge-graph-enhanced retrieval for manufacturing
> and failure-mode analysis respectively; and operator-facing studies report on adoption
> and task performance (Kernan Freire et al., 2024; Löwhagen et al., 2025). Across this
> body of work, system quality is reported in aggregate — accuracy, cost, latency, task
> outcome — and evaluation is described as predominantly manual expert review (Brehme et
> al., 2025). [CLAIM TO RE-TEST: no work in this domain reports whether an individual
> delivered answer is supported by the evidence retrieved for it, nor uses that
> determination to control delivery.] The requirement is nonetheless stated within the
> same literature: industrial outputs must be correct for the specific instance and
> auditable after the fact (Freeman et al., 2026).
