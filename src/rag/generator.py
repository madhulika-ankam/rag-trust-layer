"""
LLM answer generation.

Takes a query and retrieved chunks and generates an answer via a local LLM
running under Ollama. The prompt constrains the model to only use the
provided context, so the Trust Layer has a meaningful (if imperfect) answer
to verify — the model can still hallucinate, which is exactly what the
Trust Layer exists to catch.
"""
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

_PROMPT_TEMPLATE = """You are a manufacturing safety assistant. Answer the \
question using ONLY the information in the context below. Do not use any \
outside knowledge. If the context does not contain enough information to \
answer the question, say so explicitly instead of guessing.

Context:
{context}

Question: {query}

Answer:"""


def _format_context(chunks: list) -> str:
    parts = []
    for chunk in chunks:
        source = chunk.metadata.get("source_file", "unknown")
        page = chunk.metadata.get("page", "?")
        parts.append(f"[Source: {source} p.{page}]\n{chunk.page_content}")
    return "\n\n".join(parts)


def generate_answer(query: str, chunks: list, model: str = MODEL_NAME,
                     temperature: float = 0.0) -> str:
    """Generate an answer to `query` grounded in `chunks` via a local Ollama model."""
    prompt = _PROMPT_TEMPLATE.format(context=_format_context(chunks), query=query)

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["response"].strip()
