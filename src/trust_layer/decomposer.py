"""
Module 1: Claim Decomposer

Takes a generated answer and breaks it into atomic, individually verifiable
claims. Each claim is a single proposition that can be checked against the
retrieved document chunks by the verifier.

Handles three answer formats common in this dataset:
  - Numbered lists ("1. Step one\n2. Step two")
  - Plain paragraphs
  - Short factual answers ("4 days", "Yes")
"""
import re
import spacy

_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


# Matches numbered list items: "1.", "2.", "(1)", "(a)", "-", "•"
_LIST_ITEM_RE = re.compile(
    r"^\s*(?:\d+[\.\)]\s*|[a-zA-Z][\.\)]\s*|[-•*]\s+)", re.MULTILINE
)

# Conjunctions that may join two independent clauses worth splitting
_COORD_CONJUNCTIONS = {"and", "but", "or"}

# Claims shorter than this many words are likely fragments — merge or discard
_MIN_CLAIM_WORDS = 4


def _split_list_items(text: str) -> list[str] | None:
    """
    If the text looks like a numbered/bulleted list, return items as strings.
    Returns None if the text is not list-formatted.
    """
    matches = list(_LIST_ITEM_RE.finditer(text))
    if len(matches) < 2:
        return None

    items = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        item = text[start:end].strip()
        if item:
            items.append(item)
    return items if items else None


def _split_conjunctions(sentence: str) -> list[str]:
    """
    Split a sentence at coordinating conjunctions that join two root-level
    verb phrases. Only splits when both sides have a verb, to avoid splitting
    noun phrases like "nuts and bolts".
    """
    nlp = _get_nlp()
    doc = nlp(sentence)

    split_positions = []
    for token in doc:
        if token.text.lower() in _COORD_CONJUNCTIONS and token.dep_ == "cc":
            # The conjunction's head is the second verb; find where it starts
            head = token.head
            # Only split if head is a verb and its leftmost dependent is past
            # the conjunction (i.e., a new clause, not a noun-phrase list)
            if head.pos_ in {"VERB", "AUX"}:
                clause_start = min(t.i for t in head.subtree)
                if clause_start > token.i:
                    split_positions.append(token.i)

    if not split_positions:
        return [sentence]

    tokens = [t.text_with_ws for t in doc]
    parts = []
    prev = 0
    for pos in split_positions:
        part = "".join(tokens[prev:pos]).strip()
        if part:
            parts.append(part)
        prev = pos + 1  # skip the conjunction token
    parts.append("".join(tokens[prev:]).strip())

    return [p for p in parts if p]


def _sentences(text: str) -> list[str]:
    """Split text into sentences using spaCy."""
    nlp = _get_nlp()
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]


def _clean(claim: str) -> str:
    """Normalise whitespace and strip trailing punctuation artifacts."""
    claim = re.sub(r"\s+", " ", claim).strip()
    return claim


def decompose(answer: str) -> list[str]:
    """
    Break a generated answer into atomic verifiable claims.

    Returns a list of claim strings. For short factual answers (single word
    or phrase), returns the answer as a single claim.
    """
    answer = answer.strip()
    if not answer:
        return []

    # Try list-item splitting first
    items = _split_list_items(answer)
    if items:
        raw_claims = items
    else:
        raw_claims = _sentences(answer)

    # Further split sentences at coordinating conjunctions
    claims = []
    for raw in raw_claims:
        sub = _split_conjunctions(raw)
        claims.extend(sub)

    # Clean and filter fragments
    claims = [_clean(c) for c in claims]
    claims = [c for c in claims if len(c.split()) >= _MIN_CLAIM_WORDS]

    # If everything was filtered (e.g. a one-word answer like "Yes"), return
    # the original answer as-is — the verifier will handle it
    if not claims:
        return [answer.strip()]

    return claims
