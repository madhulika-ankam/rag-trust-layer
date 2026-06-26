import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.loader import load_documents
from src.rag.chunker import chunk_documents
from src.rag.retriever import build_vectorstore, load_vectorstore, retrieve

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


if __name__ == "__main__":
    if os.path.exists(CHROMA_DIR) and os.listdir(CHROMA_DIR):
        print("ChromaDB index found, loading...")
        vs = load_vectorstore()
    else:
        print("Building index from PDFs...")
        vs = build_index()

    query_pipeline("What are the lockout tagout requirements for energy control?", vs)
    query_pipeline("What PPE is required when working with hazardous equipment?", vs)
