"""
Module 3: Multi-Mechanism Verifier

For each claim (from the decomposer), checks it against the retrieved document
chunks using four mechanisms in a cascade:

  1. Semantic Similarity  — fast gate; skips NLI if chunk is off-topic
  2. NLI                  — entailment / neutral / contradiction
  3. Entity & Number Match — catches numerical/code precision errors
  4. Negation Detection   — catches conditional exceptions in safety text

Returns a VerificationResult per claim.
"""
import re
from dataclasses import dataclass, field

import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder

# ── Lazy-loaded models (downloaded on first use) ──────────────────────────────

_embed_model = None
_nli_model = None

EMBED_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
NLI_MODEL_NAME   = "cross-encoder/nli-deberta-v3-base"

# NLI label order for cross-encoder/nli-deberta-v3-base
# scores after softmax: [contradiction, entailment, neutral]
_NLI_CONTRADICTION = 0
_NLI_ENTAILMENT    = 1
_NLI_NEUTRAL       = 2


def _get_embed_model() -> SentenceTransformer:
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer(EMBED_MODEL_NAME)
    return _embed_model


def set_nli_model(name: str) -> None:
    """Swap the NLI checkpoint. Resets the cached model so the next call
    loads the new one. Label order is read from the model's own config
    rather than assumed — different checkpoints order them differently
    (roberta-large-mnli is contradiction/neutral/entailment)."""
    global _nli_model, NLI_MODEL_NAME
    if name != NLI_MODEL_NAME:
        NLI_MODEL_NAME = name
        _nli_model = None


def _get_nli_model() -> CrossEncoder:
    global _nli_model, _NLI_CONTRADICTION, _NLI_ENTAILMENT, _NLI_NEUTRAL
    if _nli_model is None:
        _nli_model = CrossEncoder(NLI_MODEL_NAME)
        cfg = getattr(_nli_model.model, "config", None)
        id2label = getattr(cfg, "id2label", None) or {}
        lookup = {str(v).lower(): int(k) for k, v in id2label.items()}
        if {"contradiction", "entailment", "neutral"} <= set(lookup):
            _NLI_CONTRADICTION = lookup["contradiction"]
            _NLI_ENTAILMENT = lookup["entailment"]
            _NLI_NEUTRAL = lookup["neutral"]
    return _nli_model


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class MechanismResult:
    name: str
    fired: bool
    score: float        # 0.0 – 1.0 contribution to overall score
    detail: str         # human-readable explanation


@dataclass
class VerificationResult:
    claim: str
    verdict: str        # SUPPORTED | UNSUPPORTED | CONTRADICTION
    score: float        # 0.0 – 1.0 overall confidence
    best_chunk: str     # text of the most relevant retrieved chunk
    best_chunk_source: str  # source file + page from chunk metadata
    mechanisms: list[MechanismResult] = field(default_factory=list)
    # Raw [contradiction, entailment, neutral] from the winning chunk, kept so
    # downstream analysis can compare scoring rules without re-running NLI.
    nli_probs: list[float] = field(default_factory=list)


# ── Thresholds ────────────────────────────────────────────────────────────────

SIMILARITY_GATE      = 0.25   # below this → skip NLI, mark UNSUPPORTED
CONTRADICTION_THRESH = 0.50   # NLI contradiction prob above this → CONTRADICTION
ENTAILMENT_THRESH    = 0.50   # NLI entailment prob above this → claim is supported
SUPPORTED_SCORE      = 0.60   # final combined score above this → SUPPORTED


# ── Mechanism 1: Semantic Similarity ─────────────────────────────────────────

def _semantic_similarity(claim: str, chunk_text: str) -> float:
    model = _get_embed_model()
    embeddings = model.encode([claim, chunk_text], convert_to_numpy=True)
    # Cosine similarity
    a, b = embeddings[0], embeddings[1]
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


# ── Mechanism 2: NLI ──────────────────────────────────────────────────────────

# Granularity of the premise handed to the NLI model.
#
#   "chunk"     the whole retrieved chunk (~512 chars, 4-5 sentences)
#   "sentence"  each sentence separately, aggregated by per-label max
#
# The NLI model is fine-tuned on SNLI/MultiNLI — SINGLE SENTENCE pairs — so a
# multi-sentence premise dilutes the one sentence that bears on the claim.
# Operating at sentence granularity and aggregating is the central finding of
# SummaC (Laban et al., 2022).
#
# SETTLED 2026-10-14. This default was "chunk" while run_verification.py
# overrode it to "sentence", so the library default was NOT the configuration
# the evaluation validated. Sentence wins on both test sets:
#
#   perturbation benchmark, held-out test split (n=150)
#       sentence  BA 0.919   AUC 0.975
#       chunk     BA 0.873   AUC 0.930
#
#   the 30 human-labelled answers
#                        good      false   fabrication   SUPPORTED
#                        delivered ESCALATE withheld      claims
#       sentence         6/13      0/13     3/4           211/429
#       chunk            4/13      1/13     2/4           167/429
#
# The two sets disagreed before the decomposer was fixed, and chunk looked
# better on real claims. That was an artefact: claims were long enough that
# the length effect swamped the comparison. The comparison only became valid
# once claims were short, which is itself worth reporting — granularity
# choice and decomposition granularity interact, and measuring one while the
# other is broken gives the wrong answer.
#
# The deciding case is q42, an answer the author marked as containing
# fabrication: chunk granularity returns ANSWER on it, at full confidence.
NLI_GRANULARITY = "sentence"

_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
MIN_NLI_SENT_CHARS = 15   # low enough to keep short real sentences
                          # ("Power must be disconnected." is 27 chars);
                          # high enough to drop "NOTE:", "See Figure 3." etc.


def _split_for_nli(text: str) -> list[str]:
    """
    Split a chunk into NLI-sized premises.

    Falls back to the whole chunk when there is no usable sentence boundary —
    PDF-extracted text often runs together, and an empty premise list would
    silently drop the evidence entirely.
    """
    text = " ".join(text.split())
    parts = [s.strip() for s in _SENT_SPLIT_RE.split(text)]
    parts = [s for s in parts if len(s) >= MIN_NLI_SENT_CHARS]
    return parts or [text]


def _softmax(logits: np.ndarray) -> np.ndarray:
    exp = np.exp(logits - logits.max())
    return exp / exp.sum()


def _nli_scores(claim: str, chunk_text: str,
                granularity: str | None = None) -> np.ndarray:
    """
    Return [contradiction, entailment, neutral] for a claim against evidence.

    In "chunk" mode these are softmax probabilities and sum to 1.

    In "sentence" mode the chunk is split and the claim scored against each
    sentence; the returned vector is the full softmax distribution of the
    sentence with the HIGHEST ENTAILMENT. This follows SummaC-ZS, and it
    keeps the three values a genuine probability distribution.

    An earlier version took a per-label maximum instead, so that a
    contradiction in any sentence could trigger ESCALATE. Measured on the
    302-row perturbation set that proved far too permissive: with ~5
    sentences per chunk there are five chances at a spurious contradiction,
    CONTRADICTION verdicts rose from 80 to 146, and retention of true claims
    fell from 87.3% to 73.4%.

    KNOWN LIMITATION, to state in Chapter 6: a contradiction carried by a
    sentence other than the best-entailing one is not surfaced.
    """
    model = _get_nli_model()
    mode = granularity or NLI_GRANULARITY

    if mode != "sentence":
        raw = model.predict([(chunk_text, claim)])  # premise, hypothesis
        # CrossEncoder returns raw logits; apply softmax
        return _softmax(np.array(raw[0]))

    sentences = _split_for_nli(chunk_text)
    # One batched call — looping would make this ~5x slower for no reason.
    raw = np.atleast_2d(np.array(model.predict([(s, claim) for s in sentences])))
    probs = np.vstack([_softmax(row) for row in raw])
    best = int(np.argmax(probs[:, _NLI_ENTAILMENT]))
    return probs[best]


# ── Mechanism 3: Entity & Number Matching ─────────────────────────────────────

# Patterns for safety-critical values in claims
_NUMBER_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?\s*"
    r"(?:°[CF]?|degrees?|rpm|lbs?|kg|psi|bar|volts?|amps?|db|%|mm|cm|m\b|ft\b|"
    r"inches?|hours?|days?|minutes?|seconds?)",
    re.IGNORECASE,
)
_CODE_PATTERN = re.compile(
    r"\b(?:OSHA|CFR|ISO|ANSI|NFPA|EN)\s*\d[\d\.\-]*\b",
    re.IGNORECASE,
)


def _extract_critical_values(text: str) -> list[str]:
    """Extract numbers with units and regulatory codes from text."""
    values = _NUMBER_PATTERN.findall(text)
    values += _CODE_PATTERN.findall(text)
    return [v.strip().lower() for v in values]


def _entity_match(claim: str, chunk_text: str) -> MechanismResult:
    claim_values = _extract_critical_values(claim)
    if not claim_values:
        return MechanismResult("entity_match", fired=False, score=1.0,
                               detail="no critical values in claim")

    chunk_lower = chunk_text.lower()
    matched = [v for v in claim_values if v in chunk_lower]
    miss    = [v for v in claim_values if v not in chunk_lower]

    if not claim_values:
        ratio = 1.0
    else:
        ratio = len(matched) / len(claim_values)

    detail = (
        f"matched {len(matched)}/{len(claim_values)}: {matched}"
        + (f" | missing: {miss}" if miss else "")
    )
    # Penalty: each missing critical value halves the score
    score = ratio
    return MechanismResult("entity_match", fired=True, score=score, detail=detail)


# ── Mechanism 4: Negation Detection ──────────────────────────────────────────

_NEGATION_RE = re.compile(
    r"\b(not|never|no\b|do not|don't|must not|should not|cannot|can't|"
    r"prohibited|forbidden|disallowed|except|unless|avoid)\b",
    re.IGNORECASE,
)


def _negation_check(claim: str, chunk_text: str) -> MechanismResult:
    claim_has_negation = bool(_NEGATION_RE.search(claim))
    chunk_has_negation = bool(_NEGATION_RE.search(chunk_text))

    # Four cases. The guard below must test BOTH flags: gating only on
    # `claim_has_negation` made the fourth case unreachable, which is the
    # case this mechanism exists for — evidence carrying a conditional
    # exception ("unless", "except") that the claim silently drops.
    if not claim_has_negation and not chunk_has_negation:
        return MechanismResult("negation", fired=False, score=1.0,
                               detail="no negation in claim or evidence")

    if claim_has_negation and chunk_has_negation:
        return MechanismResult("negation", fired=True, score=1.0,
                               detail="negation present in both claim and evidence")

    if claim_has_negation and not chunk_has_negation:
        return MechanismResult("negation", fired=True, score=0.4,
                               detail="claim has negation but evidence does not — possible contradiction")

    return MechanismResult("negation", fired=True, score=0.8,
                           detail="evidence has negation/exception but claim does not — "
                                  "possible omitted condition")


# ── Core cascade ──────────────────────────────────────────────────────────────

def verify_claim(claim: str, chunks: list) -> VerificationResult:
    """
    Verify one claim against all retrieved chunks.
    chunks: list of LangChain Document objects (with .page_content and .metadata)
    """
    best_score     = -1.0  # lower than any real score, so a legitimately
                            # evaluated chunk that scores 0.0 still gets kept
    best_chunk_doc = None
    best_sim       = 0.0
    best_nli_probs = None
    best_mechanisms = []

    # Contradiction is tracked ACROSS ALL CHUNKS, independently of which chunk
    # wins on score.
    #
    # A contradicting chunk is assigned combined = 0.0, so it always loses the
    # max to any non-contradicting chunk, and best_nli_probs then belongs to a
    # chunk that by construction did NOT contradict. With k=5 that made
    # ESCALATE — the safety-critical decision — effectively unreachable:
    # measured 0 of 101 claims above CONTRADICTION_THRESH at answer level,
    # against 43 of 302 at claim level where k=1. The unit tests missed it
    # because they pass a single chunk.
    #
    # A contradiction in the retrieved evidence must surface, even if another
    # chunk happens to score higher. WHICH chunk is allowed to raise one is
    # the question Step 3 settled: only the chunk the retriever ranked most
    # similar to the claim. See the verdict block below for the measurements.
    contradiction_sim = -1.0
    contradiction_p_at_top_sim = 0.0
    contradicting_source = None
    contradicting_probs = None

    for chunk in chunks:
        chunk_text = chunk.page_content

        # ── Step 1: Semantic similarity gate ──────────────────────────────
        sim = _semantic_similarity(claim, chunk_text)
        if sim < SIMILARITY_GATE:
            continue

        # ── Step 2: NLI ───────────────────────────────────────────────────
        nli_probs = _nli_scores(claim, chunk_text)
        contradiction_p = nli_probs[_NLI_CONTRADICTION]
        entailment_p    = nli_probs[_NLI_ENTAILMENT]

        if sim > contradiction_sim:
            contradiction_sim = sim
            contradiction_p_at_top_sim = contradiction_p
            contradicting_source = chunk
            contradicting_probs = nli_probs

        # Immediate contradiction — flag and keep as candidate
        if contradiction_p > CONTRADICTION_THRESH:
            combined = 0.0  # contradiction → score 0
        else:
            # Weighted combination: 30% similarity, 70% NLI entailment
            combined = 0.30 * sim + 0.70 * entailment_p

        # ── Step 3: Entity matching ───────────────────────────────────────
        entity_result = _entity_match(claim, chunk_text)

        # ── Step 4: Negation detection ────────────────────────────────────
        negation_result = _negation_check(claim, chunk_text)

        # Apply penalties from entity and negation
        if entity_result.fired:
            combined *= entity_result.score  # missing values reduce score
        if negation_result.fired:
            combined *= negation_result.score

        if combined > best_score:
            best_score      = combined
            best_chunk_doc  = chunk
            best_sim        = sim
            best_nli_probs  = nli_probs
            best_mechanisms = [
                MechanismResult("semantic_similarity", fired=True,
                                score=sim,
                                detail=f"cosine similarity = {sim:.3f}"),
                MechanismResult("nli", fired=True,
                                score=entailment_p,
                                detail=(f"entailment={entailment_p:.3f}, "
                                        f"contradiction={contradiction_p:.3f}, "
                                        f"neutral={nli_probs[_NLI_NEUTRAL]:.3f}")),
                entity_result,
                negation_result,
            ]

    # ── No chunk passed the similarity gate ───────────────────────────────
    if best_chunk_doc is None:
        return VerificationResult(
            claim=claim,
            verdict="UNSUPPORTED",
            score=0.0,
            best_chunk="",
            best_chunk_source="none",
            mechanisms=[MechanismResult("semantic_similarity", fired=True,
                                        score=0.0,
                                        detail="all chunks below similarity gate")],
        )

    # ── Determine verdict: SUPPORT FIRST, TOP-SIMILARITY CONTRADICTION ────
    #
    # Two decisions, each measured rather than reasoned.
    #
    # (1) Support is checked BEFORE contradiction. NLI has no "irrelevant"
    #     label: given a claim and an unrelated passage it must still choose
    #     entailment / contradiction / neutral, and matching structure with
    #     different specifics — "remove the two screws M" against "remove the
    #     four screws N" — reads as CONTRADICTION rather than neutral.
    #
    # (2) Only the MOST SIMILAR chunk may raise a contradiction. Taking the
    #     maximum over all k=5 chunks lets any passage about a different
    #     procedure veto the claim. Measured over the 30 answers the author
    #     read and labelled, and over all 429 claims:
    #
    #       rule               false ESCALATE   CONTRADICTION
    #                          on 13 fully-good   claims /429
    #       winning chunk only        0                 1     unreachable
    #       top similarity            0                11     <- this
    #       second-highest            2                11
    #       max, threshold 0.9        2                20
    #       max over all chunks       3                40
    #
    #     Every rule delivers the same 5 of 13 fully-good answers, withholds
    #     the same 3 of 4 containing fabrication and delivers the same 1 of 7
    #     off-target ones. The ESCALATE rule changes NOTHING except how often
    #     a sound answer is accused of contradicting the manual, so the rule
    #     that never does that and still fires is the right one.
    #
    # KNOWN LIMITATION for Chapter 6: if two documents genuinely disagree and
    # the more similar one supports the claim, the disagreement is not
    # surfaced. Rare in a corpus of three largely non-overlapping manuals;
    # real nonetheless.
    contradiction_p = contradiction_p_at_top_sim
    if best_score >= SUPPORTED_SCORE:
        verdict = "SUPPORTED"
    elif contradiction_p > CONTRADICTION_THRESH:
        verdict = "CONTRADICTION"
    else:
        verdict = "UNSUPPORTED"

    def _src(doc):
        return (doc.metadata.get("source_file", "unknown")
                + " p." + str(doc.metadata.get("page", "?")))

    # Cite the contradicting chunk when there is one — that is the evidence a
    # safety engineer needs to see, not the chunk that scored highest.
    cited = (contradicting_source
             if verdict == "CONTRADICTION" and contradicting_source is not None
             else best_chunk_doc)
    source = _src(cited)

    # Report the probabilities of the chunk the verdict is actually based on.
    # Reporting the top-scoring chunk's numbers alongside a CONTRADICTION
    # verdict derived from a different chunk would make the score unable to
    # explain the decision — which is the opposite of the auditability this
    # mechanism exists to provide.
    reported_probs = (contradicting_probs
                      if verdict == "CONTRADICTION" and contradicting_probs is not None
                      else best_nli_probs)

    return VerificationResult(
        claim=claim,
        verdict=verdict,
        score=round(best_score, 4),
        best_chunk=cited.page_content,
        best_chunk_source=source,
        mechanisms=best_mechanisms,
        nli_probs=[float(x) for x in reported_probs],
    )


def verify(claims: list[str], chunks: list) -> list[VerificationResult]:
    """Verify all claims from the decomposer against the retrieved chunks."""
    return [verify_claim(claim, chunks) for claim in claims]
