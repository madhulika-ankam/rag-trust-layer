#!/usr/bin/env python3
"""
verify_citations.py — resolve a citation against the arXiv and Crossref APIs
and print it in the format of docs/thesis/literature-review/citations.md.

WHY
    Chapter 2 cites 37 papers. A citation that was typed from memory is a
    citation that can be wrong in the viva, and "I think it was ACL 2023" is
    not an answer. Every entry in citations.md came from an API response;
    this script is how new ones join it.

    Fields the API does not return are printed as UNVERIFIED rather than
    filled in by inference. That is the whole point.

USAGE
    python -m src.verify_citations "Sentence-BERT: Sentence Embeddings"
    python -m src.verify_citations --arxiv 1908.10084
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ARXIV = "https://export.arxiv.org/api/query"
CROSSREF = "https://api.crossref.org/works"
UA = {"User-Agent": "thesis-citation-check/1.0 (mailto:research@example.edu)"}
NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def _get(url: str) -> bytes:
    return urllib.request.urlopen(
        urllib.request.Request(url, headers=UA), timeout=30).read()


def arxiv_lookup(title: str | None, arxiv_id: str | None) -> dict | None:
    if arxiv_id:
        q = f"id_list={urllib.parse.quote(arxiv_id)}&max_results=1"
    else:
        q = ("search_query=" + urllib.parse.quote(f'ti:"{title}"')
             + "&max_results=3")
    root = ET.fromstring(_get(f"{ARXIV}?{q}"))
    entries = root.findall("a:entry", NS)
    if not entries:
        return None
    e = entries[0]
    text = lambda tag: (e.findtext(tag, default="", namespaces=NS) or "").strip()
    doi_el = e.find("arxiv:doi", NS)
    jref = e.find("arxiv:journal_ref", NS)
    comment = e.find("arxiv:comment", NS)
    return {
        "title": re.sub(r"\s+", " ", text("a:title")),
        "authors": [a.findtext("a:name", default="", namespaces=NS).strip()
                    for a in e.findall("a:author", NS)],
        "id": text("a:id"),
        "published": text("a:published")[:10],
        "updated": text("a:updated")[:10],
        "doi": (doi_el.text or "").strip() if doi_el is not None else None,
        "journal_ref": (jref.text or "").strip() if jref is not None else None,
        "comment": re.sub(r"\s+", " ", (comment.text or "").strip())
                   if comment is not None else None,
    }


def crossref_lookup(title: str, doi: str | None = None) -> dict | None:
    if doi:
        url = f"{CROSSREF}/{urllib.parse.quote(doi)}"
        try:
            item = json.loads(_get(url))["message"]
        except Exception:
            return None
    else:
        url = f"{CROSSREF}?query.bibliographic={urllib.parse.quote(title)}&rows=3"
        items = json.loads(_get(url))["message"]["items"]
        if not items:
            return None
        # Only accept a near-exact title match — Crossref will happily return
        # a loosely related paper, and a plausible wrong citation is worse
        # than none.
        norm = lambda s: re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()
        item = next((i for i in items
                     if i.get("title") and norm(i["title"][0]) == norm(title)), None)
        if item is None:
            return None
    cont = item.get("container-title") or []
    date = item.get("published", {}).get("date-parts", [[None]])[0]
    return {
        "title": (item.get("title") or [""])[0],
        "venue": cont[0] if cont else None,
        "publisher": item.get("publisher"),
        "year": date[0] if date else None,
        "doi": item.get("DOI"),
        "type": item.get("type"),
        "page": item.get("page"),
        "volume": item.get("volume"),
    }


def report(label: str, title: str | None, arxiv_id: str | None) -> None:
    print(f"\n{'=' * 74}\n{label}\n{'=' * 74}")
    ax = None
    try:
        ax = arxiv_lookup(title, arxiv_id)
    except Exception as exc:
        print(f"  arXiv lookup FAILED: {exc}")
    if ax:
        print(f"  arXiv title : {ax['title']}")
        print(f"  authors     : {'; '.join(ax['authors'])}")
        print(f"  arXiv id    : {ax['id']}")
        print(f"  submitted   : {ax['published']}   updated: {ax['updated']}")
        print(f"  arXiv DOI   : {ax['doi'] or 'none on record'}")
        print(f"  journal_ref : {ax['journal_ref'] or 'none on record'}")
        print(f"  comment     : {ax['comment'] or 'none'}")
    else:
        print("  arXiv       : NO MATCH (may be pre-arXiv or non-arXiv venue)")

    cr = None
    try:
        cr = crossref_lookup(ax["title"] if ax else title,
                             ax["doi"] if ax else None)
    except Exception as exc:
        print(f"  Crossref lookup FAILED: {exc}")
    if cr:
        bits = [cr.get("venue"), f"vol {cr['volume']}" if cr.get("volume") else None,
                f"pp. {cr['page']}" if cr.get("page") else None,
                str(cr["year"]) if cr.get("year") else None]
        print(f"  CROSSREF    : {' — '.join(b for b in bits if b)}")
        print(f"  publisher   : {cr.get('publisher')}")
        print(f"  DOI         : {cr.get('doi')}")
        status = "PUBLISHED"
    elif ax and ax.get("comment") and re.search(
            r"accept|to appear|camera.?ready|proceedings|published (as|at|in)",
            ax["comment"], re.I):
        status = "ACCEPTED"
        print("  CROSSREF    : no exact title match")
    elif ax:
        status = "PREPRINT"
        print("  CROSSREF    : no exact title match")
    else:
        status = "UNVERIFIED"
    print(f"  STATUS      : {status}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("title", nargs="?", default=None)
    ap.add_argument("--arxiv", default=None)
    ap.add_argument("--batch", action="store_true",
                    help="resolve the six works Chapters 2 and 3 depend on")
    args = ap.parse_args()

    if args.batch:
        for label, title, aid in [
            ("BUMP — perturbation benchmark precedent (Ma et al.)",
             "BUMP: A Benchmark of Unfaithful Minimal Pairs for Meta-Evaluation of Faithfulness Metrics", None),
            ("FactCC — the other perturbation precedent (Kryscinski et al.)",
             "Evaluating the Factual Consistency of Abstractive Text Summarization", None),
            ("Sentence-BERT — the embedder (Reimers & Gurevych)",
             "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks", None),
            ("DeBERTaV3 — the NLI backbone (He et al.)",
             "DeBERTaV3: Improving DeBERTa using ELECTRA-Style Pre-Training with Gradient-Disentangled Embedding Sharing", None),
            ("Geifman & El-Yaniv 2017 — selective prediction",
             "Selective Classification for Deep Neural Networks", None),
            ("El-Yaniv & Wiener 2010 — selective classification foundations",
             "On the Foundations of Noise-free Selective Classification", None),
        ]:
            report(label, title, aid)
        return

    if not args.title and not args.arxiv:
        ap.error("give a title, an --arxiv id, or --batch")
    report(args.title or args.arxiv, args.title, args.arxiv)


if __name__ == "__main__":
    main()
