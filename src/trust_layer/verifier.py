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


def _get_nli_model() -> CrossEncoder:
    global _nli_model
    if _nli_model is None:
        _nli_model = CrossEncoder(NLI_MODEL_NAME)
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

def _nli_scores(claim: str, chunk_text: str) -> np.ndarray:
    """Return softmax probabilities [contradiction, entailment, neutral]."""
    model = _get_nli_model()
    raw = model.predict([(chunk_text, claim)])  # premise, hypothesis
    # CrossEncoder returns raw logits; apply softmax
    logits = np.array(raw[0])
    exp = np.exp(logits - logits.max())
    return exp / exp.sum()


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

    if not claim_has_negation:
        return MechanismResult("negation", fired=False, score=1.0,
                               detail="no negation in claim")

    if claim_has_negation and chunk_has_negation:
        return MechanismResult("negation", fired=True, score=1.0,
                               detail="negation present in both claim and evidence")

    if claim_has_negation and not chunk_has_negation:
        return MechanismResult("negation", fired=True, score=0.4,
                               detail="claim has negation but evidence does not — possible contradiction")

    return MechanismResult("negation", fired=True, score=0.8,
                           detail="evidence has negation but claim does not")


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

    # ── Determine verdict ─────────────────────────────────────────────────
    contradiction_p = best_nli_probs[_NLI_CONTRADICTION]
    if contradiction_p > CONTRADICTION_THRESH:
        verdict = "CONTRADICTION"
    elif best_score >= SUPPORTED_SCORE:
        verdict = "SUPPORTED"
    else:
        verdict = "UNSUPPORTED"

    source = (
        best_chunk_doc.metadata.get("source_file", "unknown")
        + " p."
        + str(best_chunk_doc.metadata.get("page", "?"))
    )

    return VerificationResult(
        claim=claim,
        verdict=verdict,
        score=round(best_score, 4),
        best_chunk=best_chunk_doc.page_content,
        best_chunk_source=source,
        mechanisms=best_mechanisms,
    )


def verify(claims: list[str], chunks: list) -> list[VerificationResult]:
    """Verify all claims from the decomposer against the retrieved chunks."""
    return [verify_claim(claim, chunks) for claim in claims]
