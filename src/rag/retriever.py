from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

EMBED_MODEL = "sentence-transformers/all-mpnet-base-v2"
CHROMA_DIR = "data/chroma"


def build_vectorstore(chunks: list) -> Chroma:
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
    )
    print(f"Stored {len(chunks)} chunks in ChromaDB at {CHROMA_DIR}")
    return vectorstore


def load_vectorstore() -> Chroma:
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    return Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)


def retrieve(query: str, vectorstore: Chroma, k: int = 5) -> list:
    results = vectorstore.similarity_search(query, k=k)
    return results
