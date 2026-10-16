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

# Normalisation is on by default. Set False to reproduce results produced
# before 2026-10-14.
NORMALISE = True

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


# ── Claim normalisation ──────────────────────────────────────────────────────
#
# Splitting is not enough. The verifier is asked "is this statement supported
# by this evidence?", which only has an answer if what it is handed IS a
# statement. Raw decomposer output is frequently not:
#
#     "According to the context, it is explicitly stated on page 30 of the
#      User Manual: 'Very strong magnetic fields can damage the robot."
#
# That is a direct quotation from the manual, and it was verified as
# UNSUPPORTED — because of the words wrapped around it. Stripped to
# "Very strong magnetic fields can damage the robot." it verifies as
# SUPPORTED against identical evidence.
#
# Measured on the 32 claims belonging to 13 answers a human judged fully
# grounded: normalising PHRASING ONLY, with no change of meaning and no
# change of evidence, moved the flag rate from 53% to 30% and contradictions
# from 4 to 1. The verifier scores AUC 0.976 on well-formed claims; the gap
# was what Module 1 was handing it.
#
# Each rule below was written before being applied, so every transformation
# is auditable.

# R1 — meta-framing. States where information came from, not what is true of
# the machine. The verifier has nothing to check it against.
_META_PREFIX_RE = re.compile(
    r"^\s*(?:"
    r"according to|as (?:stated|mentioned|described|shown) in|based on|per"
    r")\s+(?:the\s+)?[^,:]{0,80}?[,:]\s*", re.IGNORECASE)

# Framing often arrives CHAINED — "According to X, it is explicitly stated on
# page N: <claim>" — so a second pattern strips the inner layer, and both are
# applied until the text stops changing.
_META_INNER_RE = re.compile(
    r"^\s*it\s+(?:is|was)\s+(?:explicitly\s+|clearly\s+)?"
    r"(?:stated|mentioned|noted|written|specified)\s+"
    r"(?:(?:on|in)\s+[^,:]{0,60})?[,:]\s*", re.IGNORECASE)

# R2 — conversational connectors carried over from the model's prose style.
_CONNECTOR_RE = re.compile(
    r"^\s*(?:so|therefore|thus|hence|in summary|overall)\s*,?\s*"
    r"(?:yes|no)?\s*,?\s*", re.IGNORECASE)

# R4 — claims about the DOCUMENT rather than about the machine. Dropped, not
# rewritten: there is nothing in the evidence for them to be checked against.
_DOC_LOCATION_RE = re.compile(
    r"^\s*(?:this|that|it)\s+(?:is|was|can be)\s+"
    r"(?:mentioned|stated|found|listed|described|explained|shown|covered)"
    r"\s+(?:in|on|at)\b",
    re.IGNORECASE)

# R7 — claims about what the documents DO NOT say. R4 drops claims about
# where information sits; this drops claims about its absence. They are the
# same kind of thing — a statement about the corpus, not about the machine —
# and they fail in a worse way. "There is no specific mention of a Bridgeport
# mill in the provided manual" is handed to NLI alongside a manual that talks
# about Bridgeport mills, and comes back CONTRADICTION at p=0.98. The model
# is being penalised for admitting it does not know, which is the one
# behaviour this system should encourage.
#
# run_verification.looks_like_a_decline() already catches an answer that is
# ENTIRELY a decline. This catches the same move made in one sentence of an
# otherwise substantive answer, which that check cannot see.
_NO_INFO_RE = re.compile(
    r"(?:"
    r"there\s+(?:is|are)\s+no\s+(?:\w+\s+){0,2}?"
    r"(?:mention|information|indication|reference|details?|specifics?|"
    r"instructions?|steps?|guidance|procedures?)\b"
    r"|no\s+(?:further|additional|other|more)\s+information\s+is\s+"
    r"(?:provided|available|given|mentioned)"
    r"|(?:is|are)\s+not\s+(?:\w+\s+){0,2}?"
    r"(?:mentioned|stated|specified|provided|listed|available|included|covered|"
    r"addressed|described)\b"
    r"|(?:context|manual|document|documents|manuals|text)s?\s+"
    r"(?:does|do)\s+not\s+"
    r"(?:mention|provide|contain|specify|state|include|cover|address)\b"
    r"|i\s+(?:cannot|can\s?not|can't|could\s?not|couldn't|am\s+unable\s+to|"
    r"was\s+unable\s+to|do\s+not|don't|did\s+not|didn't)\s+"
    r"(?:provide|answer|determine|find|confirm|give|see|locate)\b"
    r"|(?:do|does)(?:\s+not|n't)\s+seem\s+to\s+"
    r"(?:provide|mention|contain|cover|address|include|discuss)\b"
    r"|this\s+information\s+is\s+not\s+available"
    # "It doesn't mention anything about ..." — the same move with a pronoun
    # standing in for the document.
    r"|(?:it|this|that|they)\s+(?:does|do)(?:\s+not|n't)\s+"
    r"(?:mention|provide|contain|specify|state|include|cover|address)\b"
    # "The manuals only discuss X" / "The inspection plan only covers Y" —
    # a statement about the corpus's scope, not about the machine.
    r"|(?:context|manual|document|text|section|plan|information|source)s?\s+"
    r"(?:provided\s+|given\s+)?(?:only|just)\s+"
    r"(?:discuss|cover|provide|mention|include|address|describe|state)"
    r"(?:es|s)?\b"
    r"|(?:the\s+)?(?:context|manual|document|text|source|section|chapter|"
    r"plan)s?\s+(?:on\s+[^,.]{0,40}\s+)?(?:appears?|seems?)\s+to\b"
    r")", re.IGNORECASE)

# R5 — inline source citations. Read as content by the verifier, which then
# fails to find "Source: KneeMill-Complete-Manual.pdf p.2" in the evidence.
_CITATION_RE = re.compile(
    r"\s*\((?:source\s*:\s*)?[^()]*?p\.?\s*\d+[^()]*\)|"
    # One level of nesting, for "(Source: OSHA Technical Manual (OTM) -
    # Section IV ... .pdf p.9)", which the flat pattern above cannot match.
    r"\s*\(source\s*:[^()]*(?:\([^()]*\)[^()]*)*\)|"
    # Square-bracket form. Left in, "[Source: KneeMill-Complete-Manual.pdf
    # p.30]" was parsed as a noun phrase and became the SUBJECT of a claim:
    # "KneeMill-Complete-Manual.pdf p.30 is the Spindle Brake C."
    r"\s*\[(?:source\s*:\s*)?[^\[\]]*?p\.?\s*\d+[^\[\]]*\]|"
    r"\s*\[source\s*:[^\[\]]*\]", re.IGNORECASE)

# R6 — markdown emphasis and leading punctuation left by the splitter.
_MARKUP_RE = re.compile(r"""\*\*|\*|^[\s"'`]+""")


def normalise_claim(claim: str) -> str | None:
    """
    Reshape a decomposer output into something the verifier can judge.

    Returns None for claims that should be DROPPED — statements about where
    information sits in a document are not claims about the world, and
    verifying them is meaningless.
    """
    c = _MARKUP_RE.sub("", claim).strip()
    if _DOC_LOCATION_RE.match(c):          # R4
        return None
    # R1 — applied until stable, since framing arrives in layers
    for _ in range(3):
        before = c
        c = _META_PREFIX_RE.sub("", c)
        c = _META_INNER_RE.sub("", c)
        if c == before:
            break
        if _DOC_LOCATION_RE.match(c):      # R4 may only become visible here
            return None
    if _NO_INFO_RE.search(c):               # R7
        return None
    c = _CONNECTOR_RE.sub("", c)            # R2
    c = _CITATION_RE.sub("", c)             # R5
    c = re.sub(r"\s+", " ", c).strip(""" "'`""")
    if c and c[0].islower():
        c = c[0].upper() + c[1:]
    return c or None


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


# ── Atomic clause splitting ──────────────────────────────────────────────────
#
# Sentence boundaries are not small enough. Measured over all 392 verified
# claims, entailment collapses as the CLAIM — the NLI hypothesis — lengthens:
#
#     claim words    n   mean entailment   % SUPPORTED   mean similarity
#     0-8           35        0.686            63%            0.391
#     8-12          62        0.699            65%            0.513
#     16-20         58        0.375            36%            0.535
#     26+           95        0.162            13%            0.631
#
#     Spearman, length vs entailment   rho -0.353   p 5.7e-13
#     Spearman, length vs similarity   rho +0.370   p 3.9e-14
#
# The two correlations run in OPPOSITE directions, which rules out the obvious
# confound — long claims are MORE on topic and LESS entailed, so the effect is
# on the NLI model and not on relevance. Confirmed causally: rewriting qid 23
# from 23 words to 6 without changing its meaning moved entailment from 0.000
# to 0.996.
#
# Three structures pack a second proposition into one sentence. Each is
# detached with its subject carried over, so what is emitted still stands
# alone — the same thing _merge_parent_child does for nested list items:
#
#   relative clause   "The guard, which must be removed, covers the belt."
#                  -> "The guard covers the belt."  +
#                     "The guard must be removed."
#   appositive        "Setting 9, the Dimensioning setting, selects units."
#                  -> "Setting 9 selects units."  +
#                     "Setting 9 is the Dimensioning setting."
#   coordinated verb  "Disconnect the power and remove the cover."
#                  -> "Disconnect the power."  +  "Remove the cover."
#
# WHAT IS DELIBERATELY NOT SPLIT: a conditional, temporal or causal
# subordinate clause. "When MM is selected, programmed units are millimetres"
# does NOT entail "Programmed units are millimetres" — detaching the condition
# manufactures a claim the evidence may well contradict, which is precisely
# the failure this layer exists to catch (see the negation mechanism, which
# penalises a claim for dropping a condition the evidence states). Conditions
# are DISTRIBUTED across conjuncts instead of discarded:
#
#     "When X, do A and do B"  ->  "When X, do A."  +  "When X, do B."
#
# Restrictive relative clauses ("the agents you can use include ...") are left
# alone for the same reason: the clause picks out WHICH thing is meant, so
# removing it broadens the claim. Only comma-set-off, non-restrictive clauses
# are detached.

# Sentences at or below this length are already in the band where entailment
# holds, so they are returned untouched rather than risking a bad split.
_NO_SPLIT_WORDS = 12

# Relativisers that can introduce a detachable non-restrictive clause
_RELATIVISERS = {"which", "who", "that"}


def _render(doc, idxs) -> str:
    """Rebuild readable text from a set of token indices of `doc`."""
    kept = sorted(idxs)
    parts = []
    for n, i in enumerate(kept):
        tok = doc[i]
        parts.append(tok.text)
        if n + 1 == len(kept):
            break
        # Original spacing holds only where the two tokens were adjacent in
        # the source. Across a removal a space is required, or the words
        # either side of the cut fuse: "The R8 colletis tightened".
        if kept[n + 1] == i + 1 and tok.whitespace_ == "":
            continue
        parts.append(" ")
    out = re.sub(r"\s+", " ", "".join(parts))
    out = re.sub(r"\s+([,.;:)])", r"\1", out)
    out = re.sub(r"(\()\s+", r"\1", out)
    out = re.sub(r"(?:,\s*){2,}", ", ", out)       # commas left by a removal
    out = re.sub(r"\s*,\s*([.;:])", r"\1", out)
    return out.strip(" ,;:")


def _ensure_sentence(text: str) -> str:
    """Capitalise and terminate a fragment so it reads as a statement."""
    text = text.strip()
    if not text:
        return text
    if text[0].islower():
        text = text[0].upper() + text[1:]
    if text[-1] not in ".!?":
        text += "."
    return text


def _noun_phrase(doc, head, exclude: set[int]) -> set[int]:
    """
    Token indices of the noun phrase headed by `head` — determiners,
    adjectives and compounds to its left, but not trailing modifiers, which
    may themselves be the piece being detached.
    """
    idxs = {head.i}
    for child in head.lefts:
        if child.dep_ in {"det", "amod", "compound", "nummod", "poss", "nmod"}:
            idxs |= {t.i for t in child.subtree}
    return idxs - exclude


def _preceded_by_comma(doc, span: set[int]) -> bool:
    start = min(span)
    return start > 0 and doc[start - 1].text == ","


def _extract_relcl(doc, tok):
    """
    Detach a non-restrictive relative clause as its own claim.

    Returns (claim_text, token_indices_to_remove) or None when the clause is
    restrictive, has no relativiser subject, or hangs off something that is
    not a noun — all cases where detaching would change what is being said.
    """
    span = {t.i for t in tok.subtree}
    if not _preceded_by_comma(doc, span):
        return None                                  # restrictive — leave it
    antecedent = tok.head
    if antecedent.pos_ not in {"NOUN", "PROPN"}:
        return None

    relativiser = next(
        (c for c in tok.children
         if c.dep_ in {"nsubj", "nsubjpass"}
         and (c.tag_ in {"WDT", "WP"} or c.lower_ in _RELATIVISERS)),
        None,
    )
    if relativiser is None:
        return None                                  # object relative — skip

    subject = _noun_phrase(doc, antecedent, span)
    body = span - {t.i for t in relativiser.subtree}
    if not subject or not body:
        return None
    return f"{_render(doc, subject)} {_render(doc, body)}", span


def _extract_appos(doc, tok):
    """
    Turn a comma-set-off appositive into an explicit "X is Y." claim.
    """
    span = {t.i for t in tok.subtree}
    if not _preceded_by_comma(doc, span):
        return None
    head = tok.head
    if head.pos_ not in {"NOUN", "PROPN"}:
        return None
    # A comma-separated list of nouns — "water, 70% isopropyl alcohol, 10%
    # ethanol alcohol, and naphtha" — is parsed with the second item as an
    # appositive of the first. Emitting "Water is 70% isopropyl alcohol."
    # would FABRICATE a claim, so coordination anywhere in the phrase vetoes
    # the rule.
    if any(c.dep_ == "conj" for c in head.children) or \
       any(c.dep_ == "conj" for c in tok.children):
        return None
    subject = _noun_phrase(doc, head, span)
    if not subject:
        return None
    copula = "are" if head.tag_ in {"NNS", "NNPS"} else "is"
    return f"{_render(doc, subject)} {copula} {_render(doc, span)}", span


def _split_clauses(sentence: str) -> list[str]:
    """
    Detach non-restrictive relative clauses and appositives from a sentence,
    emitting each as a standalone claim with the subject carried over.
    """
    if len(sentence.split()) <= _NO_SPLIT_WORDS:
        return [sentence]

    doc = _get_nlp()(sentence)
    keep = set(range(len(doc)))
    extracted: list[str] = []

    for tok in doc:
        if tok.dep_ == "relcl":
            piece = _extract_relcl(doc, tok)
        elif tok.dep_ == "appos":
            piece = _extract_appos(doc, tok)
        else:
            continue
        if piece is None:
            continue
        text, span = piece
        if not span <= keep:
            continue                                 # nested — already taken
        # Drop BOTH commas that set the clause off. Leaving the closing one
        # behind produced "The spindle guard, covers the drive belt."
        start, end = min(span), max(span)
        drop = set(span)
        if doc[start - 1].text == ",":
            drop.add(start - 1)
        if end + 1 < len(doc) and doc[end + 1].text == ",":
            drop.add(end + 1)
        extracted.append(text)
        keep -= drop

    if not extracted:
        return [sentence]

    parts = [_render(doc, keep)] + extracted
    parts = [_ensure_sentence(p) for p in parts if p.strip()]
    if not all(_is_wellformed(p) for p in parts):
        return [sentence]              # a split that loses text or grammar
    return parts


# Function words a conjunct cannot stand without once it is detached from the
# conjunct that carried them: "Disconnect the power and remove the cover" needs
# no carry, but "it allows the operator TO stop X, make Y and perform Z" does.
_CARRY_DEPS = {"nsubj", "nsubjpass", "expl", "aux", "auxpass", "neg", "mark"}

# A conjunct that already has a subject of its own does not need the first
# conjunct's, and the labels are not interchangeable — spaCy may call one
# `nsubj` and the other `nsubjpass`. Comparing raw labels let both through
# and produced "...safety functions are are the basis of the strategy."
_CARRY_GROUP = {
    "nsubj": "subject", "nsubjpass": "subject", "expl": "subject",
    "aux": "auxiliary", "auxpass": "auxiliary",
    "neg": "negation", "mark": "marker", "advcl": "condition",
}

# Rounds of conjunct splitting. Each round splits one coordination per
# sentence, so a three-way list needs a second pass over the pieces.
_SPLIT_ROUNDS = 3


def _contiguous(idxs: set[int], doc=None) -> bool:
    """
    Contiguous as a block of words. With `doc` given, punctuation sitting in
    the gap is ignored — the comma in "When X is engaged, disconnect ..."
    belongs to the root, not to the condition, and must not stop the
    condition from being recognised as one leading block.
    """
    if not idxs:
        return False
    if doc is None:
        return max(idxs) - min(idxs) + 1 == len(idxs)
    gap = set(range(min(idxs), max(idxs) + 1)) - idxs
    return all(doc[i].is_punct for i in gap)


def _opens_with_marker(doc, clause) -> bool:
    """True when a subordinate clause is introduced by "when", "if", "after"
    and the like. spaCy labels these `mark` or, for wh-words, `advmod`, so
    the dependency label alone is not enough to recognise one."""
    first = min(t.i for t in clause.subtree)
    return doc[first].pos_ == "SCONJ" or doc[first].dep_ == "mark"


def _conjunct_pieces(doc, head) -> list[set[int]] | None:
    """
    Token index sets for one coordination headed by `head`, or None when the
    coordination is not safely splittable.

    The shared context copied into each conjunct must be a CONTIGUOUS opening
    block, and each conjunct must itself be contiguous. Gluing non-adjacent
    spans together is what produced "The documents only provide information
    on to loosen the drawbar." and "It is ensure that the robot has been
    tested" — grammatical wreckage that the NLI model then read as a
    contradiction. A claim the decomposer cannot assemble cleanly is worth
    less than the long claim it came from.
    """
    conjs = [c for c in head.children
             if c.dep_ == "conj" and c.pos_ in {"VERB", "AUX"}]
    # Without and/but/or this is not a plain coordination of two statements.
    if not conjs or not any(c.dep_ == "cc" and c.lower_ in _COORD_CONJUNCTIONS
                            for c in head.children):
        return None

    conj_spans = [{t.i for t in c.subtree} for c in conjs]
    if not all(_contiguous(s) for s in conj_spans):
        return None
    taken = set().union(*conj_spans)
    subtree = {t.i for t in head.subtree}
    tail = len(doc) - 1 - len(_trailing_punct(doc))
    if not _contiguous(subtree) or max(subtree) < tail:
        # The head does not govern the rest of the sentence, so there is
        # material on the far side of the coordination that belongs to
        # neither conjunct. Leave it alone.
        return None

    carried: dict[str, set[int]] = {}
    for child in head.children:
        if child.i >= head.i:
            continue                                 # only what precedes
        if child.dep_ in _CARRY_DEPS:
            carried[_CARRY_GROUP[child.dep_]] = {t.i for t in child.subtree} - taken
        elif child.dep_ == "advcl" and _opens_with_marker(doc, child):
            # A leading "When X, ..." governs every conjunct, so it is copied
            # into each rather than left behind on the first.
            span = {t.i for t in child.subtree} - taken
            after = max(span) + 1
            if after < len(doc) and doc[after].text == ",":
                span.add(after)                      # keep the comma with it
            carried["condition"] = span

    all_carried = set().union(*carried.values()) if carried else set()
    if all_carried and not _contiguous(all_carried | {head.i}, doc):
        return None

    cc_tokens = {c.i for c in head.children if c.dep_ == "cc"}
    pieces = [subtree - taken - cc_tokens]
    for conj, span in zip(conjs, conj_spans):
        # Carry over only what this conjunct does not already have of its
        # own. Copying a negation the conjunct already carries produced
        # "Do not do not operate the spindle brake".
        own = {_CARRY_GROUP.get(c.dep_) for c in conj.children}
        add = set().union(*(idx for group, idx in carried.items()
                            if group not in own)) if carried else set()
        pieces.append(add | span)
    return pieces


def _trailing_punct(doc) -> set[int]:
    idxs = set()
    for t in reversed(doc):
        if t.is_punct:
            idxs.add(t.i)
        else:
            break
    return idxs


def _is_wellformed(text: str) -> bool:
    """
    A detached piece has to read as a statement. Re-parsing is the cheapest
    check that it does: a piece with no verbal root, or one that trails off
    on a preposition or an infinitive marker, was cut mid-phrase.
    """
    doc = _get_nlp()(text)
    words = [t for t in doc if not t.is_punct]
    if len(words) < _MIN_CLAIM_WORDS:
        return False
    root = next((t for t in doc if t.dep_ == "ROOT"), None)
    if root is None or root.pos_ not in {"VERB", "AUX"}:
        return False
    if words[-1].pos_ in {"ADP", "PART", "DET", "CCONJ", "SCONJ", "AUX"}:
        return False
    # An immediately repeated word is the signature of a carried function
    # word the conjunct already had: "are are the basis", "do not do not".
    lowered = [t.lower_ for t in words]
    if any(a == b for a, b in zip(lowered, lowered[1:])):
        return False
    return True


def _split_conjunctions(sentence: str) -> list[str]:
    """
    Split coordinated verb phrases into separate claims, carrying the shared
    subject, auxiliaries and any leading condition into each piece.

    Noun-phrase coordination ("nuts and bolts") is left alone: those conjuncts
    are nouns, not verbs, so they never match here.
    """
    out = [sentence]
    for _ in range(_SPLIT_ROUNDS):
        nxt: list[str] = []
        for part in out:
            nxt.extend(_split_conjunctions_once(part))
        if len(nxt) == len(out):
            break                                    # fixpoint
        out = nxt
    return out


def _split_conjunctions_once(sentence: str) -> list[str]:
    if len(sentence.split()) <= _NO_SPLIT_WORDS:
        return [sentence]

    doc = _get_nlp()(sentence)
    # Only the sentence's own root verb. Coordination inside a complement
    # ("verify that A, that B and that C") splits into pieces that begin with
    # a dangling "That ..." and have lost their matrix verb; measured on the
    # 161 answers those pieces read as contradictions far more often than the
    # long claim they replaced.
    heads = [t for t in doc if t.dep_ == "ROOT" and t.pos_ in {"VERB", "AUX"}]
    for head in heads:
        pieces = _conjunct_pieces(doc, head)
        if pieces is None:
            continue
        parts = [_ensure_sentence(_render(doc, p)) for p in pieces]
        parts = [p for p in parts if p.strip()]
        if len(parts) < 2 or not all(_is_wellformed(p) for p in parts):
            continue                   # a split that loses text or grammar
        return parts
    return [sentence]


def _sentences(text: str) -> list[str]:
    """Split text into sentences using spaCy."""
    nlp = _get_nlp()
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]


def _clean(claim: str) -> str:
    """Normalise whitespace and strip trailing punctuation artifacts."""
    claim = re.sub(r"\s+", " ", claim).strip()
    claim = re.sub(r"\s+([,.;:])", r"\1", claim)
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
    raw_claims = items if items else [answer]

    # Sentence-split INSIDE each list item. A list item is not one sentence:
    # the regex gives the final item everything to the end of the answer, so
    # any closing prose was swallowed into it — q126 came out as a single
    # 123-word "claim" made of six sentences. Running the sentence splitter
    # over every item costs nothing and removes the worst outliers.
    sentences = []
    for raw in raw_claims:
        # Citations and markup are removed BEFORE the parse, not after. Left
        # in, "[Source: KneeMill-Complete-Manual.pdf p.30]" parses as a noun
        # phrase and the splitter makes it the subject of a claim, which no
        # later cleanup can undo: "KneeMill-Complete-Manual.pdf p.30 is the
        # Spindle Brake C."
        raw = _MARKUP_RE.sub("", _CITATION_RE.sub(" ", raw))
        sentences.extend(_sentences(raw))

    # Then go below the sentence: detach relative clauses and appositives,
    # and distribute shared subjects across coordinated verbs.
    claims = []
    for sent in sentences:
        for piece in _split_clauses(sent):
            claims.extend(_split_conjunctions(piece))

    # Clean, normalise, and filter fragments
    claims = [_clean(c) for c in claims]
    dropped_as_non_claims = False
    if NORMALISE:
        kept = []
        for c in claims:
            n = normalise_claim(c)
            if n:
                kept.append(n)
            else:
                dropped_as_non_claims = True
        claims = kept
    claims = [c for c in claims if len(c.split()) >= _MIN_CLAIM_WORDS]

    if not claims:
        # Everything was DROPPED as a non-claim — the answer talks about the
        # documents, not the machine. Returning the raw answer here would
        # hand the verifier exactly the text R4 and R7 just removed, and
        # "There is no mention of a Bridgeport mill in the manual" comes back
        # as a CONTRADICTION at p=0.98 against a manual about Bridgeport
        # mills. An answer with nothing to check has no claims.
        if dropped_as_non_claims:
            return []
        # Nothing was dropped, so the answer was simply too short to clear
        # the fragment filter ("Yes", "4 days"). That IS the claim.
        return [answer.strip()]

    return claims
