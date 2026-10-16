import shutil
import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

EMBED_MODEL = "sentence-transformers/all-mpnet-base-v2"
CHROMA_DIR = "data/chroma"


def build_vectorstore(chunks: list, persist_dir: str = CHROMA_DIR) -> Chroma:
    """
    Build a fresh Chroma index from `chunks`, replacing any existing index
    at CHROMA_DIR. Chroma.from_documents() appends to an existing persisted
    collection rather than replacing it, so the old directory is removed
    first — otherwise re-running this after removing/renaming source PDFs
    leaves stale, orphaned chunks permanently mixed in with the new ones.
    """
    if os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)

    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
    )
    print(f"Stored {len(chunks)} chunks in ChromaDB at {persist_dir}")
    return vectorstore


def load_vectorstore(persist_dir: str = CHROMA_DIR) -> Chroma:
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    return Chroma(persist_directory=persist_dir, embedding_function=embeddings)


def retrieve(query: str, vectorstore: Chroma, k: int = 5) -> list:
    results = vectorstore.similarity_search(query, k=k)
    return results
