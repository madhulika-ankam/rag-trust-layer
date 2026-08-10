import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.loader import load_documents
from src.rag.chunker import chunk_documents
from src.rag.retriever import build_vectorstore, load_vectorstore, retrieve
from src.rag.generator import generate_answer
from src.trust_layer.decomposer import decompose
from src.trust_layer.verifier import verify
from src.trust_layer.scorer import score
from src.trust_layer.decision import decide
from src.trust_layer.reporter import generate_report, format_report

CHROMA_DIR = "data/chroma"


def build_index():
    docs = load_documents("data/raw")
    chunks = chunk_documents(docs)
    vectorstore = build_vectorstore(chunks)
    return vectorstore


def query_pipeline(query: str, vectorstore=None):
    if vectorstore is None:
        vectorstore = load_vectorstore()
    chunks = retrieve(query, vectorstore)
    print(f"\nQuery: {query}")
    print(f"Top {len(chunks)} retrieved chunks:\n")
    for i, chunk in enumerate(chunks, 1):
        source = chunk.metadata.get("source_file", "unknown")
        page = chunk.metadata.get("page", "?")
        print(f"[{i}] {source} — page {page}")
        print(chunk.page_content[:300])
        print()
    return chunks


def run_pipeline(query: str, vectorstore=None):
    """
    Full pipeline: retrieve -> generate answer -> decompose -> verify ->
    score -> decide -> report. This is the real end-to-end path — every
    other entry point in this file only exercises part of it.
    """
    if vectorstore is None:
        vectorstore = load_vectorstore()

    chunks = retrieve(query, vectorstore)
    answer = generate_answer(query, chunks)
    claims = decompose(answer)
    results = verify(claims, chunks)
    trust = score(results)
    decision = decide(trust)
    return generate_report(query, answer, results, trust, decision)


if __name__ == "__main__":
    if os.path.exists(CHROMA_DIR) and os.listdir(CHROMA_DIR):
        print("ChromaDB index found, loading...")
        vs = load_vectorstore()
    else:
        print("Building index from PDFs...")
        vs = build_index()

    for q in [
        "What are the lockout tagout requirements for energy control?",
        "What PPE is required when working with hazardous equipment?",
    ]:
        report = run_pipeline(q, vs)
        print(format_report(report))
        print("\n" + "=" * 80 + "\n")
