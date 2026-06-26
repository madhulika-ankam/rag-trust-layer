from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader


def load_documents(pdf_dir: str = "data/raw") -> list:
    docs = []
    for pdf_path in Path(pdf_dir).glob("*.pdf"):
        loader = PyPDFLoader(str(pdf_path))
        pages = loader.load()
        for page in pages:
            page.metadata["source_file"] = pdf_path.name
        docs.extend(pages)
        print(f"Loaded {len(pages)} pages from {pdf_path.name}")
    return docs
