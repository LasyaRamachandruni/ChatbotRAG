import json
import re

import pytest

import llm as llm_module
from rag import REFUSAL, SYSTEM_PROMPT, answer, check_grounding, split_sentences
from retrieval import Retriever, build_retriever, load_chunks


@pytest.fixture(scope="module")
def retriever():
    return Retriever(load_chunks())


class FakeLLM:
    """Stands in for a real model: records the prompt and returns a canned reply."""

    def __init__(self, reply):
        self.reply = reply
        self.calls = []

    def __call__(self, system, user):
        self.calls.append((system, user))
        return self.reply(user) if callable(self.reply) else self.reply


def test_generated_answer_cites_retrieved_sources(retriever):
    fake = FakeLLM("The dean of the library is Michael Meth [1].")
    result = answer("Who is the dean?", retriever, fake)
    assert result.mode == "generated"
    assert result.text == "The dean of the library is Michael Meth [1]."
    assert result.sources == [(1, "org_chart_sjsu_king_library.md")]
    system, prompt = fake.calls[0]
    assert system == SYSTEM_PROMPT
    assert "[1] (from org_chart_sjsu_king_library.md)" in prompt
    assert "Dean: Michael Meth" in prompt


def test_prompt_only_contains_retrieved_chunks(retriever):
    fake = FakeLLM("Sharon Thompson runs the KLEVR Lab [1].")
    answer("Who do I contact about the KLEVR Lab?", retriever, fake)
    prompt = fake.calls[0][1]
    assert "KLEVR Lab" in prompt
    assert "Michael Meth" not in prompt  # unrelated chunks are not sent


def test_ungrounded_sentences_are_dropped(retriever):
    fake = FakeLLM(
        "Michael Meth is the dean [1]. "
        "The library is open 24 hours during finals. "  # no citation
        "Lisa Josefik is his executive assistant [9]."  # cites a chunk we never retrieved
    )
    result = answer("Who is the dean?", retriever, fake)
    assert result.text == "Michael Meth is the dean [1]."
    assert result.dropped == [
        "The library is open 24 hours during finals.",
        "Lisa Josefik is his executive assistant [9].",
    ]


def test_answer_with_no_grounded_sentences_is_refused(retriever):
    result = answer("Who is the dean?", retriever, FakeLLM("I think it is probably someone nice."))
    assert result.mode == "refused"
    assert result.text == REFUSAL


@pytest.mark.parametrize("question", [
    "What are the library hours?",
    "How do I renew a book?",
    "What's the wifi password?",
])
def test_out_of_scope_question_is_refused_without_calling_the_llm(retriever, question):
    fake = FakeLLM("should not be used [1].")
    result = answer(question, retriever, fake)
    assert result.mode == "refused"
    assert "Ask a Librarian" in result.text
    assert "library.sjsu.edu/ask-librarian" in result.text
    assert fake.calls == []


def test_llm_saying_not_found_is_refused(retriever):
    result = answer("Who is the dean?", retriever, FakeLLM("NOT_FOUND"))
    assert result.mode == "refused"


def test_falls_back_to_quoting_without_api_key(retriever, monkeypatch):
    for var in ["LLM_PROVIDER", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY",
                "GOOGLE_API_KEY", "OLLAMA_HOST"]:
        monkeypatch.delenv(var, raising=False)
    assert llm_module.get_llm() is None
    result = answer("How do I request a parking permit?", retriever, None)
    assert result.mode == "quoted"
    assert result.text == "Internal permit request form for SJSU guests. [1]"
    assert result.sources == [(1, "sjsu_parking_permit_request.md")]


def test_provider_chosen_from_env(monkeypatch):
    for var in ["LLM_PROVIDER", "OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY", "OLLAMA_HOST"]:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    name, _ = llm_module.get_llm()
    assert name == "anthropic/claude-haiku-4-5"
    monkeypatch.setenv("LLM_PROVIDER", "gemini")  # chosen but no Gemini key
    assert llm_module.get_llm() is None
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("LLM_MODEL", "mistral")
    assert llm_module.get_llm()[0] == "ollama/mistral"


def test_sentence_splitting_keeps_citations_with_their_sentence():
    text = "Ask Dr. Becker [2]. The lab is in room 1. [1]\nEmail sharon.thompson@sjsu.edu [1]."
    assert split_sentences(text) == [
        "Ask Dr. Becker [2].", "The lab is in room 1. [1]", "Email sharon.thompson@sjsu.edu [1].",
    ]
    kept, dropped = check_grounding("A [1, 2]. B [0]. C [3].", n_sources=2)
    assert kept == ["A [1, 2]."]
    assert dropped == ["B [0].", "C [3]."]


def test_index_is_saved_and_reused(tmp_path):
    first = build_retriever(index_dir=tmp_path, mode="bm25")
    saved = list(tmp_path.glob("chunks-*.json"))
    assert len(saved) == 1
    # A second build reads the saved file instead of re-chunking.
    data = json.loads(saved[0].read_text())
    data[0]["text"] = "## Marker\nloaded from disk"
    saved[0].write_text(json.dumps(data))
    second = build_retriever(index_dir=tmp_path, mode="bm25")
    assert second.chunks[0].text == "## Marker\nloaded from disk"
    assert len(second.chunks) == len(first.chunks)


def test_hybrid_retrieval_with_fake_embeddings():
    chunks = load_chunks()

    def embed(texts):  # 1-d "embedding" that puts cars and parking close together
        return [[1.0] if "park" in t.lower() or "car" in re.findall(r"[a-z]+", t.lower()) else [0.0]
                for t in texts]

    hybrid = Retriever(chunks, embedder=embed)
    hits = hybrid.search("Where can I leave my car?")  # no word in common with the KB
    assert hybrid.mode == "hybrid"
    assert hits[0].chunk.source == "sjsu_parking_permit_request.md"
