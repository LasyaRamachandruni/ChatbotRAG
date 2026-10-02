"""Pick the most relevant line from retrieved knowledge-base text.

The app runs without an LLM: the vector index finds the most similar documents,
and this picks the single line in them that shares the most words with the question.
"""

from __future__ import annotations

import re

STOPWORDS = {
    "a", "an", "and", "are", "can", "do", "does", "for", "how", "i", "in", "is", "it",
    "me", "my", "of", "on", "or", "please", "the", "to", "what", "when", "where", "who",
    "with", "you", "your", "about", "tell", "get",
}


def _words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 1 and w not in STOPWORDS}


def _clean(line: str) -> str:
    return re.sub(r"\*\*|__|^[#\-\s]+", "", line).strip()


def best_answer(question: str, texts: list[str], fallback_chars: int = 300) -> str:
    """Return the knowledge-base line that best answers the question.

    Each content line is scored by the question words it contains, plus half a point
    per question word in its section heading, so "Who is the dean?" picks
    "Dean: ..." under "## Dean's Office" rather than the heading itself. Headings are
    only returned when a section has no content lines. Ties go to the earlier (more
    similar) document. With no overlap at all, the start of the top document is returned.
    """
    keywords = _words(question)
    best_line, best_score = "", 0.0
    for text in texts:
        heading_words: set[str] = set()
        heading, heading_has_content = "", True
        candidates: list[tuple[float, str]] = []
        for line in text.splitlines():
            plain = _clean(line)
            if not plain:
                continue
            if line.lstrip().startswith("#"):
                if not heading_has_content and heading:
                    candidates.append((len(keywords & heading_words), heading))
                heading, heading_words, heading_has_content = plain, _words(plain), False
                continue
            heading_has_content = True
            candidates.append((len(keywords & _words(plain)) + 0.5 * len(keywords & heading_words), plain))
        if not heading_has_content and heading:
            candidates.append((len(keywords & heading_words), heading))
        for score, line in candidates:
            if score > best_score:
                best_line, best_score = line, score
    if best_score > 0:
        return best_line
    if texts and texts[0].strip():
        return texts[0].strip()[:fallback_chars]
    return "No relevant information found."
