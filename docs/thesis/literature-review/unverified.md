# Unverified — what could not be confirmed

**This file is a deliverable, not a failure log.** It is what makes the rest of the
review trustworthy: everything here is explicitly *not* confirmed, so nothing in the
other files is silently guessed.

Last updated **2026-10-15**.

---

## A. Cited in the project by author-year only — no ID, title or venue anywhere

> **Update 2026-10-14.** Six of these were resolved with
> `python -m src.verify_citations --batch` and written into `citations.md`
> under **Category 14**. They were prioritised because Chapters 2 and 3 are
> load-bearing on them:
>
> | work | outcome |
> |---|---|
> | **BUMP** (Ma et al.) | ✅ PUBLISHED — arXiv 2212.09955, ACL 2023, DOI 10.18653/v1/2023.acl-long.716 |
> | **FactCC** (Kryscinski et al.) | ✅ PUBLISHED — arXiv 1910.12840, **EMNLP 2020** (not 2019), DOI 10.18653/v1/2020.emnlp-main.750 |
> | **Sentence-BERT** (Reimers & Gurevych) | ✅ PUBLISHED — arXiv 1908.10084, EMNLP-IJCNLP 2019, DOI 10.18653/v1/d19-1410 |
> | **DeBERTaV3** (He et al.) | ✅ ACCEPTED — arXiv 2111.09543, ICLR 2023 per the authors' comment; no Crossref DOI |
> | **Geifman & El-Yaniv (2017)** | ⚠ arXiv 1705.08500 confirmed; venue NOT confirmed — **moves to §B**, not resolved |
> | **El-Yaniv & Wiener (2010)** | ❌ still UNVERIFIED — not on arXiv, no Crossref match; JMLR coverage is patchy. Verify by hand or cite Geifman & El-Yaniv (2017) instead |
>
> The remaining entries in this section are untouched.


These appear in `EVALUATION_PLAN.md`, `CONTEXT.md` or the thesis chat with no locator.
None has yet been resolved to a real record.

| Referred to as | Used for | Status |
|---|---|---|
| **BUMP (Ma et al., 2023)** | the named precedent for the 302-row perturbation set | no title, no arXiv ID, no venue anywhere in the project. **Highest priority** — it is the methodological precedent for RQ3 |
| **El-Yaniv & Wiener (2010)** | origin of the risk-coverage framework | not resolved |
| **Geifman & El-Yaniv (2017)**, "Selective Classification for Deep Neural Networks" | risk-coverage formal definitions | not resolved |
| **Brodersen et al. (2010)** | balanced accuracy itself — cited *by SummaC* for the metric | not resolved |
| **FactCC (Kryscinski et al., 2020)** | on the reading list; never actually cited | not resolved. Note the surname is commonly spelled **Kryściński** |
| **Sentence-BERT (Reimers & Gurevych, EMNLP 2019)** | semantic similarity mechanism | ticked in the plan file but absent from every reference list |
| **DeBERTaV3 (He et al.)** | **the model actually run** (`deberta-v3-base`) | the project cites DeBERTa `2006.03654` instead. A different paper. Not resolved |
| **SNLI (Bowman et al., 2015)** | NLI training data | lead from RT4CHART's bibliography: EMNLP 2015, pp. 632–642. Needs ACL Anthology confirmation |
| **MultiNLI (Williams et al., NAACL 2018)** | NLI training data | not resolved |
| ARES, FaithDial, G-Eval, Chain-of-Verification, Say Less (Feng et al. 2023), RobustQA, SummEdits, HaluEval, SafetyBench, RegNLP, BioNLI, SciNLI, LegalBERT+NLI | related-work tables in the thesis chat | none resolved |
| ~~"AI Trustworthiness in Manufacturing…", MDPI *Sensors* 2025~~ | — | ✅ **RESOLVED 2026-10-15**: Ahangar, Farhat & Sivanathan, *Sensors* 25(14):4357, DOI `10.3390/s25144357` |
| "Shopfloor Terminology for RAG" (2025) | weak related work | no arXiv ID or venue recorded — **still open** |

## B. Resolved on arXiv but venue/peer-review still unconfirmed

| Paper | Issue |
|---|---|
| **Ragas** `2309.15217` | no DOI on the arXiv record. The project's prior work guessed "EACL 2024 demo track" — **unconfirmed, do not cite that venue yet.** This matters: RAGAS is now the *only* surviving comparison for Contribution 4 |
| **MedTrust-RAG** `2510.14400` | arXiv comment reads "Accepted as a short paper at **BlBM2025**" — almost certainly IEEE BIBM 2025, but the string is corrupted. Get the proceedings citation |
| **RT4CHART** `2603.27752` | bibliography reveals an ASE 2026 research-track submission. Check whether accepted before submission — it would change from preprint to published prior art |
| **Ji et al.** `2202.03629` | Crossref gives `2023-12-31`; the arXiv journal-ref string says `ACM Computing Surveys (2022)`. Cite 2023 (Crossref is authoritative) but be aware of the discrepancy |
| **Toward Epistemic Stability** `2603.10047` (ref [6]) | published in *Computer and Information Science* 19(2) by the **Canadian Center of Science and Education**. ⚠ Technically peer-reviewed, but a venue a committee may question. It carries the "auditable after the fact" requirement — consider finding a stronger source for that claim |

## C. Secondary-source leads — from RT4CHART's bibliography, not yet primary-confirmed

Twelve full citations with venues and page numbers were harvested from RT4CHART's
reference list (see `13-closest-prior-work.md` §13.4). They are high-confidence but
**second-hand**. Each needs confirmation against the ACL Anthology or ACM DL before
submission: SNLI, SummaC, FActScore, VeriScore, SAFE/Wei et al., MiniCheck, AlignScore,
ALCE/Gao et al., RAGTruth, SelfCheckGPT, LettuceDetect, Lynx.

SummaC and FActScore have since been independently confirmed (SummaC via Crossref DOI
`10.1162/tacl_a_00453`; FActScore via arXiv `2305.14251`). The other ten have not.

## D. Categories not yet searched at all

| # | Category | Note |
|---|---|---|
| ✅ | **The four manufacturing journal leads — RESOLVED 2026-10-15** (DOIs supplied by the author, all Crossref-verified): Löwhagen et al. *IJPR* `10.1080/00207543.2025.2527368`; Wan et al. *Adv. Eng. Informatics* `10.1016/j.aei.2025.103212`; Bahr et al. *J. Industrial Information Integration* `10.1016/j.jii.2025.100807`; Ahangar et al. *Sensors* `10.3390/s25144357`. Also DesignQA → *JCISE* 25(2) `10.1115/1.4067333` |
| **2** | Safety-critical & high-stakes AI | reading-list Group 5 was never populated. Zero references exist. Also unaddressed: cobot safety standards (ISO 10218, ISO/TS 15066) relevant to Contribution 6's three machines |
| **6** | Numerical reasoning & negation in NLI | **zero citations.** The thesis asserts entailment models are "known to be susceptible" and "documented to be weak" on numbers and conditional exceptions. Documented by whom is answered nowhere. This grounds Contribution 3 and RQ3 |
| **NEW** | **Domain adaptation / distribution shift for NLI on technical and regulatory text** — identified 2026-10-14 via JEDI (`05-nli-factual-consistency.md` §5.10). The verifier runs a model trained on SNLI/MNLI against OSHA and OEM documents; this is unacknowledged in Chapter 1 and uncovered by any category in this review. Candidates not yet searched: domain-adaptive pretraining, NLI transfer to specialised domains |
| **10** | Trust calibration & over-reliance | the canon (Lee & See; Parasuraman & Riley; Bansal et al.; Buçinca et al.; Vasconcelos et al.) is entirely absent. Currently rests on ref [7] alone, which §B confirms is an unreviewed preprint |

## E. Factual gaps inside the project itself

| Item | Status |
|---|---|
| **153 vs 161 questions** | Singh et al. report 153 (60 UR5e + 51 Haas + 42 Bridgeport); the file Megahed supplied has 161 rows. Unexplained. Do not smooth over — state it in the methodology |
| **Bridgeport manual version** | M-508 (2018) recorded, but the project flags the exact version as still pending from Megahed |
| **11 dataset rows** | special-character encoding errors, flagged as fixable by script |
| **BLS / BEA / Liberty Mutual primaries** | ref [1] cites four statistics second-hand through Singh et al. Three distinct primary sources are needed and **none is yet identified by name, year or report number** |
| **"you risk safety" quotation** | attributed to an unnamed participant in ref [4]. Must be verified against the published Frontiers version — whose title differs from the arXiv one (see `citations.md`) |

## A2. Second-hand citations introduced 2026-10-16

From the refusal passage in Zhang et al. (2025) — see `03-hallucination-taxonomies.md`
§3.4. All three are cited *through the survey* and none is independently resolved. Resolve
them only if the SFT-refusal contrast becomes load-bearing rather than a single sentence.

| Referred to as | For | Status |
|---|---|---|
| **Sun et al. (2023b)** — the Moss project | open-sourced SFT data containing "honest samples" | not resolved |
| **Llama Team (2024)** | refusal responses in SFT data | not resolved |
| **Wan et al. (2024)** | refusal responses in SFT data | not resolved |

## E2. New open questions from the 2026-10-15 journal upgrade

| Item | Why it matters | Action |
|---|---|---|
| **Does the published Singh et al. still report 153 questions?** | the preprint says 153, the supplied file has 161. The *Manufacturing Letters* version may have changed or resolved this | check the journal article; it determines what Chapter 5's methodology says |
| **Does the trust-calibration future-work statement survive in the published version?** | §1.3's gap argument relies on Singh et al. naming trust calibration / over- and under-reliance as their own future work. Journal revisions often rewrite future-work sections | verify in the journal version before the gap argument leans on it |
| **⚠ The manufacturing gap claim needs re-testing** | the gap statement was formed before the four journal papers were in hand. They are exactly the kind of paper that could falsify it | read the four abstracts and check whether any reports faithfulness/groundedness or gates output. See `01-manufacturing-rag.md` §1.8 |
| **Is CCSE's *Computer and Information Science* indexed?** | ref [6] carries the "auditable after the fact" requirement. CCSE appears in the Beall's-list archive; current indexing status unconfirmed | search the Web of Science Master Journal List and Scopus Source List for the journal title — two minutes, and it settles the concern either way |
| **Which DesignQA version to cite** | two exist with different titles: *JCISE* 25(2) `10.1115/1.4067333` (7 authors) and DETC 2024 `10.1115/detc2024-139024` (6 authors, omits Ataei) | cite the JCISE journal version |
| **Domain adaptation / distribution shift for NLI on technical text** | identified 2026-10-14 via JEDI — see §D | not yet searched |
| **HalluRAG's venue** | an OpenReview record exists (`openreview.net/pdf?id=pO0s74aF3R`) so it was submitted somewhere; OpenReview returns HTTP 403 from this machine | open the forum page in a browser — one minute |

## F. Corrections already confirmed — apply these

| Where | Current | Correct |
|---|---|---|
| thesis chat line 9222 | `2207.05221` = "Linguistic Calibration of LLMs" | **"Language Models (Mostly) Know What They Know"** — confirmed via arXiv API |
| thesis chat line 22480 | Zhang et al. 2023 survey, arXiv ID "not found" | **`2309.01219` = "Siren's Song in the AI Ocean: A Survey on Hallucination in Large Language Models"**, 16 authors, Yue Zhang first — confirmed |
| Chapter 1 ref [4] | arXiv title + Frontiers venue, mixed | the published Frontiers title is **different**: "Knowledge sharing in manufacturing using LLM-powered tools: user study and model benchmarking". Pick one version and cite it consistently |
| Chapter 1 ref [5] | placeholder, no authors | **Brehme, L., Dornauer, B., Ströhle, T., Ehrhart, M., & Breu, R. (2025).** KDIR / IC3K 2025 proceedings, SciTePress, pp. 110–122. DOI `10.5220/0013739500004000`. **Peer-reviewed** |
| Chapter 1 ref [6] | placeholder, no authors | **Freeman, B., Kicklighter, A., Erdman, M., & Gordon, Z. (2026).** *Computer and Information Science* 19(2), p. 1. DOI `10.5539/cis.v19n2p1`. Published — see the venue caveat in §B |
| Chapter 1 ref [7] | placeholder, no authors | **Elchafei, P., Swain, M., Masoudian, S., & Schedl, M. (2026).** arXiv `2604.09174`. **Unreviewed preprint — no DOI.** |
| Chapter 1 ref [9] | title flagged as in doubt | title is **correct** as written. Confirmed via arXiv: "On Faithfulness and Factuality in Abstractive Summarization", Maynez, Narayan, Bohnet, McDonald, ACL 2020 |
| Chapter 1 ref [10] | no page numbers | ICONAT 2025, IEEE, **pp. 1–7**, 2025-09-19. Confirmed via Crossref |
| Chapter 1 refs [1]/[3] | arXiv preprint, cited twice | **NOW PUBLISHED**: *Manufacturing Letters* **49, pp. 30–41**, DOI `10.1016/j.mfglet.2026.07.012`, Elsevier, 2026-10. Merge the duplicate entries and cite the journal version |
| ManuRAG | arXiv "(Early Version)" `2601.15434` | **NOW PUBLISHED**: Li, Dong, Ameri & Zhang, *Journal of Intelligent Manufacturing*, DOI `10.1007/s10845-026-02800-y`, 2026-03-15. Note the published author list |
