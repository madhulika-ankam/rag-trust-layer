from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(docs: list, chunk_size: int = 512, chunk_overlap: int = 64) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    print(f"Split {len(docs)} pages into {len(chunks)} chunks")
    return chunks
