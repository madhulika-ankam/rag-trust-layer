"""
Tests for LLM answer generation (src/rag/generator.py).

These call a live local Ollama server running llama3, so they're slower
than the rest of the suite and require `ollama serve` to be running with
the model pulled (`ollama pull llama3`). Assertions are kept loose since
LLM output isn't perfectly deterministic even at temperature 0.

Run with:
    source venv/bin/activate
    pytest tests/test_generator.py -v
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.generator import generate_answer


class FakeChunk:
    def __init__(self, text, source="manual.pdf", page=1):
        self.page_content = text
        self.metadata = {"source_file": source, "page": page}


def test_generate_answer_returns_nonempty_string():
    chunks = [FakeChunk("Employees must wear safety glasses at all times in the machine shop.")]
    answer = generate_answer("What eye protection is required?", chunks)

    assert isinstance(answer, str)
    assert len(answer.strip()) > 0


def test_generate_answer_uses_information_from_context():
    chunks = [FakeChunk(
        "Do not operate the Bridgeport mill spindle above 4200 RPM under any circumstances."
    )]
    answer = generate_answer("What is the maximum spindle RPM for the Bridgeport mill?", chunks)

    assert "4200" in answer


def test_generate_answer_declines_when_context_is_irrelevant():
    chunks = [FakeChunk(
        "Lockout/tagout procedures require the employer to establish an energy control program."
    )]
    answer = generate_answer("What is the boiling point of liquid nitrogen?", chunks)

    lowered = answer.lower()
    decline_signals = ["does not contain", "cannot answer", "not enough information",
                        "no information", "context does not", "doesn't contain",
                        "not provided", "unable to answer", "does not provide",
                        "don't have enough", "do not have enough", "no mention"]
    assert any(signal in lowered for signal in decline_signals), answer
