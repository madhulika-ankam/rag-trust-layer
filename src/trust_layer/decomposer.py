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


# Matches numbered list items: "1.", "2.", "(1)", "(a)", "-", "•", "+"
# Captures leading indentation so nested (sub-)items can be detected.
_LIST_ITEM_RE = re.compile(
    r"^(?P<indent>[ \t]*)(?:\d+[\.\)]\s*|[a-zA-Z][\.\)]\s*|[-•*+]\s+)", re.MULTILINE
)

# Conjunctions that may join two independent clauses worth splitting
_COORD_CONJUNCTIONS = {"and", "but", "or"}

# Claims shorter than this many words are likely fragments — merge or discard
_MIN_CLAIM_WORDS = 4


def _split_list_items(text: str) -> list[str] | None:
    """
    If the text looks like a numbered/bulleted list, return items as claim
    strings. Returns None if the text is not list-formatted.
    """
    matches = list(_LIST_ITEM_RE.finditer(text))
    if len(matches) < 2:
        return None

    raw_items = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        item_text = text[start:end].strip()
        if item_text:
            raw_items.append((len(match.group("indent")), item_text))

    return _merge_nested_items(raw_items) if raw_items else None


def _merge_parent_child(parent_text: str, child_text: str) -> str:
    """
    Join a parent list item's text with a nested child item's text so the
    child reads as a complete claim instead of a fragment, e.g. parent
    "Lockout devices shall be:" + child "Singularly identified" ->
    "Lockout devices shall be singularly identified".
    """
    parent_text = parent_text.rstrip().rstrip(":").strip()
    child_text = child_text.strip()
    if child_text and child_text[0].isupper() and not parent_text.endswith((".", "!", "?")):
        child_text = child_text[0].lower() + child_text[1:]
    return f"{parent_text} {child_text}"


def _merge_nested_items(raw_items: list[tuple[int, str]]) -> list[str]:
    """
    Merge indented sub-items with their nearest less-indented ancestor's
    text. An item whose text ends in ':' is treated as a header for its
    children (e.g. "X shall be:") and is not itself emitted as a claim —
    only its merged children are, since the header alone is an incomplete
    fragment.
    """
    items = []
    stack: list[tuple[int, str]] = []  # (indent, text used as ancestor context)

    for indent, text in raw_items:
        while stack and stack[-1][0] >= indent:
            stack.pop()

        parent_text = stack[-1][1] if stack else None
        claim_text = _merge_parent_child(parent_text, text) if parent_text else text

        is_header = text.rstrip().endswith(":")
        if not is_header:
            items.append(claim_text)

        ancestor_text = claim_text.rstrip().rstrip(":").strip() if is_header else claim_text
        stack.append((indent, ancestor_text))

    return items


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
