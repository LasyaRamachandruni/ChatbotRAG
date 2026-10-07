"""Split the knowledge base into chunks and retrieve the best ones for a question.

Chunking follows the shape of the Markdown files:
  * every row of a table becomes its own chunk, written out with its column names,
  * every section (heading + its bullet points / text) becomes one chunk.

Retrieval is BM25 by default (pure Python, no downloads). Set RETRIEVER=hybrid to
also embed chunks with all-MiniLM-L6-v2 (needs `sentence-transformers`) and merge
the two rankings with reciprocal rank fusion. The index is saved under `.index/`
and only rebuilt when a knowledge-base file changes.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

KB_DIR = Path(__file__).parent / "knowledge_base"
INDEX_DIR = Path(__file__).parent / ".index"

# Words that carry no meaning for matching. "library", "sjsu" and "king" appear in
# almost every question and chunk, so they are dropped too.
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "could", "do", "does", "for",
    "from", "has", "have", "how", "i", "if", "in", "is", "it", "its", "me", "my", "of",
    "on", "or", "our", "please", "should", "so", "that", "the", "their", "there", "this",
    "to", "up", "us", "was", "we", "what", "when", "where", "which", "who", "whom",
    "why", "will", "with", "would", "you", "your", "about", "tell", "get", "need",
    "want", "know", "any", "some", "someone", "anyone", "help", "contact", "email",
    "library", "libraries", "sjsu", "king", "s",
}

# BM25 score the top chunk needs before we treat the knowledge base as covering the
# question. One meaningful word in common with a chunk scores roughly 2-4.
MIN_BM25_SCORE = float(os.getenv("MIN_BM25_SCORE", "2.0"))
# Cosine similarity that counts as relevant in hybrid mode.
MIN_COSINE = float(os.getenv("MIN_COSINE", "0.45"))


@dataclass(frozen=True)
class Chunk:
    id: str
    source: str  # file name, used in citations
    section: str
    text: str


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float


def _stem(word: str) -> str:
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower().replace("’", "'"))
    return [_stem(w) for w in words if w not in STOPWORDS and len(w) > 1]


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def chunk_markdown(text: str, source: str) -> list[Chunk]:
    chunks: list[Chunk] = []
    title, section, body = "", "", []
    header: list[str] | None = None

    def flush() -> None:
        nonlocal body
        content = "\n".join(body).strip()
        if content:
            name = section or title
            label = f"{title} > {section}" if section and title else name
            chunks.append(Chunk(f"{source}#{len(chunks) + 1}", source, name, f"{label}\n{content}"))
        body = []

    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("#"):
            flush()
            header = None
            heading = line.lstrip("#").strip()
            if raw.startswith("# ") or not title:
                title, section = heading, ""
            else:
                section = heading
            continue
        if line.startswith("|"):
            cells = _cells(line)
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                continue  # separator row
            if header is None:
                flush()
                header = cells
                continue
            row = "; ".join(f"{h}: {c}" for h, c in zip(header, cells) if c)
            chunks.append(Chunk(f"{source}#{len(chunks) + 1}", source, cells[0], f"{title}\n{row}"))
            continue
        header = None
        if line:
            body.append(line)
    flush()
    return chunks


def load_chunks(kb_dir: Path = KB_DIR) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(kb_dir.glob("*.md")):
        chunks.extend(chunk_markdown(path.read_text(encoding="utf-8"), path.name))
    return chunks


def kb_fingerprint(kb_dir: Path = KB_DIR) -> str:
    h = hashlib.sha256()
    for path in sorted(kb_dir.glob("*.md")):
        h.update(path.name.encode())
        h.update(path.read_bytes())
    return h.hexdigest()[:16]


class BM25:
    def __init__(self, docs: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.tfs = [Counter(d) for d in docs]
        self.lens = [len(d) for d in docs]
        self.avg_len = (sum(self.lens) / len(docs)) if docs else 0.0
        df = Counter(t for d in docs for t in set(d))
        n = len(docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def scores(self, query: list[str]) -> list[float]:
        out = []
        for tf, length in zip(self.tfs, self.lens):
            s = 0.0
            for term in set(query):
                f = tf.get(term, 0)
                if f:
                    norm = self.k1 * (1 - self.b + self.b * length / self.avg_len)
                    s += self.idf[term] * f * (self.k1 + 1) / (f + norm)
            out.append(s)
        return out


class Retriever:
    """BM25 over knowledge-base chunks, optionally fused with MiniLM embeddings."""

    def __init__(self, chunks: list[Chunk], embedder=None, embeddings=None):
        self.chunks = chunks
        self.bm25 = BM25([tokenize(c.text) for c in chunks])
        self.embedder = embedder  # callable: list[str] -> 2D array of unit vectors
        self.embeddings = embeddings
        if embedder is not None and embeddings is None:
            self.embeddings = embedder([c.text for c in chunks])

    @property
    def mode(self) -> str:
        return "hybrid" if self.embedder is not None else "bm25"

    def search(self, question: str, k: int = 4) -> list[Hit]:
        """Top-k chunks, or [] when nothing in the knowledge base looks relevant."""
        lexical = self.bm25.scores(tokenize(question))
        lex_rank = sorted(range(len(self.chunks)), key=lambda i: -lexical[i])
        relevant = bool(lexical) and lexical[lex_rank[0]] >= MIN_BM25_SCORE

        if self.embedder is None:
            ranked = [i for i in lex_rank if lexical[i] > 0]
            scores = lexical
        else:
            q = self.embedder([question])[0]
            dense = [float(sum(a * b for a, b in zip(q, e))) for e in self.embeddings]
            dense_rank = sorted(range(len(self.chunks)), key=lambda i: -dense[i])
            relevant = relevant or dense[dense_rank[0]] >= MIN_COSINE
            fused = Counter()
            for rank_list in (lex_rank, dense_rank):
                for r, i in enumerate(rank_list):
                    fused[i] += 1 / (60 + r)
            ranked = [i for i, _ in fused.most_common()]
            scores = [fused[i] for i in range(len(self.chunks))]

        if not relevant:
            return []
        return [Hit(self.chunks[i], scores[i]) for i in ranked[:k]]


def _minilm_embedder():
    from sentence_transformers import SentenceTransformer  # optional dependency

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return lambda texts: model.encode(texts, normalize_embeddings=True).tolist()


def build_retriever(kb_dir: Path = KB_DIR, index_dir: Path = INDEX_DIR,
                    mode: str | None = None) -> Retriever:
    """Load the saved index for the current knowledge base, or build and save it."""
    mode = (mode or os.getenv("RETRIEVER", "bm25")).lower()
    fingerprint = kb_fingerprint(kb_dir)
    index_file = index_dir / f"chunks-{fingerprint}.json"
    if index_file.exists():
        chunks = [Chunk(**c) for c in json.loads(index_file.read_text())]
    else:
        chunks = load_chunks(kb_dir)
        index_dir.mkdir(exist_ok=True)
        index_file.write_text(json.dumps([asdict(c) for c in chunks], indent=1))

    if mode != "hybrid":
        return Retriever(chunks)

    embedder = _minilm_embedder()
    emb_file = index_dir / f"minilm-{fingerprint}.json"
    embeddings = json.loads(emb_file.read_text()) if emb_file.exists() else None
    retriever = Retriever(chunks, embedder=embedder, embeddings=embeddings)
    if embeddings is None:
        emb_file.write_text(json.dumps(retriever.embeddings))
    return retriever
