"""Retrieval -> generation -> grounding check.

1. The retriever returns the top-k knowledge-base chunks (or nothing, if no chunk
   is relevant enough, in which case we say we don't know).
2. The LLM writes a short answer using only those chunks, citing them as [1], [2].
3. check_grounding() drops every sentence that has no citation or cites a chunk
   number that was not retrieved. If nothing survives, we say we don't know.

Without an LLM the best-matching line is quoted from the retrieved chunks instead.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from answer import best_answer
from llm import LLM
from retrieval import Hit, Retriever

ASK_A_LIBRARIAN = "https://library.sjsu.edu/ask-librarian"
NOT_FOUND = "NOT_FOUND"
REFUSAL = (
    "I don't know - that isn't covered by the information I have. "
    f"Please try Ask a Librarian: {ASK_A_LIBRARIAN}"
)

SYSTEM_PROMPT = f"""You answer questions about the SJSU Dr. Martin Luther King, Jr. Library.
Use ONLY the numbered sources you are given. Do not use outside knowledge.
Answer in at most three short sentences. End every sentence with the number of the
source(s) it comes from, like [1] or [1][2].
If the sources do not answer the question, reply with exactly {NOT_FOUND}."""


@dataclass
class Answer:
    text: str
    mode: str  # "generated", "quoted" or "refused"
    sources: list[tuple[int, str]] = field(default_factory=list)  # (number, file name)
    dropped: list[str] = field(default_factory=list)  # sentences removed by the check


def build_prompt(question: str, hits: list[Hit]) -> str:
    blocks = [f"[{n}] (from {h.chunk.source})\n{h.chunk.text}" for n, h in enumerate(hits, 1)]
    return "Sources:\n\n" + "\n\n".join(blocks) + f"\n\nQuestion: {question}"


_CITATION = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")
_LEADING_CITATIONS = re.compile(r"((?:\[\d+(?:\s*,\s*\d+)*\]\s*)+)[.,;]?\s*")
_ABBREVIATIONS = ("Dr.", "Mr.", "Ms.", "Mrs.", "Jr.", "Sr.", "St.", "e.g.", "i.e.")


def cited_numbers(sentence: str) -> set[int]:
    return {int(n) for group in _CITATION.findall(sentence) for n in group.split(",")}


def split_sentences(text: str) -> list[str]:
    pieces = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    sentences: list[str] = []
    for piece in (p.strip() for p in pieces):
        if not piece:
            continue
        if sentences and sentences[-1].endswith(_ABBREVIATIONS):
            sentences[-1] += " " + piece  # "Dr. Smith" was split in two
            continue
        lead = _LEADING_CITATIONS.match(piece)
        if sentences and lead:
            # citation written after the period belongs to the previous sentence
            sentences[-1] += " " + lead.group(1).strip()
            piece = piece[lead.end():].strip(" .,;")
        if piece:
            sentences.append(piece)
    return sentences


def check_grounding(text: str, n_sources: int) -> tuple[list[str], list[str]]:
    """Split into (kept, dropped) sentences.

    A sentence is kept only if it cites at least one source and every number it
    cites is between 1 and n_sources.
    """
    kept, dropped = [], []
    for sentence in split_sentences(text):
        nums = cited_numbers(sentence)
        if nums and all(1 <= n <= n_sources for n in nums):
            kept.append(sentence)
        else:
            dropped.append(sentence)
    return kept, dropped


def _quote(question: str, hits: list[Hit]) -> Answer:
    texts = [h.chunk.text for h in hits]
    line = best_answer(question, texts)
    n = next((i for i, t in enumerate(texts, 1) if line in t.replace("**", "")), 1)
    return Answer(f"{line} [{n}]", "quoted", [(n, hits[n - 1].chunk.source)])


def answer(question: str, retriever: Retriever, llm: LLM | None = None, k: int = 4) -> Answer:
    hits = retriever.search(question, k=k)
    if not hits:
        return Answer(REFUSAL, "refused")
    if llm is None:
        return _quote(question, hits)

    raw = llm(SYSTEM_PROMPT, build_prompt(question, hits)).strip()
    if NOT_FOUND in raw:
        return Answer(REFUSAL, "refused")
    kept, dropped = check_grounding(raw, len(hits))
    if not kept:
        return Answer(REFUSAL, "refused", dropped=dropped)
    used = sorted({n for s in kept for n in cited_numbers(s)})
    return Answer(" ".join(kept), "generated", [(n, hits[n - 1].chunk.source) for n in used], dropped)
