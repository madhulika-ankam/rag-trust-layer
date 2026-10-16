"""
LLM answer generation.

Takes a query and retrieved chunks and generates an answer via a local LLM
running under Ollama.

THREE PROMPTS, because the prompt turned out to be load-bearing.

    The original prompt (now "guarded") tells the model to use only the
    context AND to say so explicitly rather than guess when the context is
    insufficient. That second instruction is an ABSTENTION instruction — one
    of the trust layer's four decisions, implemented in the prompt, inside
    what EVALUATION_PLAN.md calls the unverified baseline.

    24 of 161 answers declined outright under it, and a hand review of 30
    answers found 0 ungrounded and 0 contradicted. The baseline was already
    doing a weaker version of the contribution's job, which is why there was
    almost nothing left for the trust layer to catch.

    Separating the prompt into three levels turns that confound into a
    measurable condition:

        minimal   container only — genuine vanilla RAG, the Config A that
                  EVALUATION_PLAN.md describes
        grounded  + "use only the context, no outside knowledge";
                  grounded generation with NO decision layer. Arguably the
                  fairest baseline for this thesis, since the decision layer
                  is precisely what the trust layer adds.
        guarded   + "say so instead of guessing" — the original, and the one
                  every result before 2026-10-13 was produced under.
"""
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

_PROMPTS = {
    # Container only. No instruction about behaviour — the form used in most
    # introductory RAG implementations, and the closest thing to the
    # unverified baseline Config A is meant to represent.
    "minimal": """Context:
{context}

Question: {query}

Answer:""",

    # Grounding instruction, but NO instruction to abstain.
    "grounded": """You are a manufacturing safety assistant. Answer the \
question using ONLY the information in the context below. Do not use any \
outside knowledge.

Context:
{context}

Question: {query}

Answer:""",

    # The original: grounding AND abstention.
    "guarded": """You are a manufacturing safety assistant. Answer the \
question using ONLY the information in the context below. Do not use any \
outside knowledge. If the context does not contain enough information to \
answer the question, say so explicitly instead of guessing.

Context:
{context}

Question: {query}

Answer:""",
}

PROMPT_MODE = "guarded"   # default preserves every result produced so far


def _format_context(chunks: list) -> str:
    parts = []
    for chunk in chunks:
        source = chunk.metadata.get("source_file", "unknown")
        page = chunk.metadata.get("page", "?")
        parts.append(f"[Source: {source} p.{page}]\n{chunk.page_content}")
    return "\n\n".join(parts)


def generate_answer(query: str, chunks: list, model: str = MODEL_NAME,
                     temperature: float = 0.0,
                     prompt_mode: str | None = None) -> str:
    """Generate an answer to `query` grounded in `chunks` via a local Ollama model."""
    mode = prompt_mode or PROMPT_MODE
    if mode not in _PROMPTS:
        raise ValueError(f"prompt_mode must be one of {sorted(_PROMPTS)}, got {mode!r}")
    prompt = _PROMPTS[mode].format(context=_format_context(chunks), query=query)

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
