# SJSU King Library Chatbot

[![CI](https://github.com/LasyaRamachandruni/ChatbotRAG/actions/workflows/ci.yml/badge.svg)](https://github.com/LasyaRamachandruni/ChatbotRAG/actions/workflows/ci.yml)

## Problem

Staff and students at the Dr. Martin Luther King, Jr. Library at San José State University ask the same questions again and again: who runs a service, who to contact for help, which internal form to use (parking permits, event funding). The answers live in a few internal documents. The chatbot should answer from those documents only, say where each answer came from, and say "I don't know" (with a link to Ask a Librarian) when the documents don't cover the question.

There are two versions:

| Version | How it answers | Runs where |
|---|---|---|
| **RAG chatbot** (`chatbot_app.py`) | Retrieves knowledge-base chunks, has an LLM write a short answer from only those chunks with citations, then checks every sentence is cited | Python / Streamlit; OpenAI, Anthropic, Gemini or a local Ollama model. Without a key it quotes the knowledge base |
| **Web chatbot** (`index.html`, `script.js`) | Hand-written keyword rules (no retrieval, no LLM) | Any browser; embeddable in Google Sites |

## Result

`evals/questions.jsonl` has 33 questions written the way staff and students would ask them: 28 that the knowledge base covers, each labeled with the file and table row / section that answers it, and 5 out-of-scope questions (hours, fines, study rooms, printing, tuition) that should be refused.

Results with BM25 retrieval, from [evals/results.md](evals/results.md) (36 chunks, 33 questions). Produced by `python evals/run_eval.py`, which is offline and deterministic (pure Python, no model, no GPU), so any CPU gives the same output; CI re-runs it on every push and fails if the output differs from the committed file.

| Metric | Result |
|---|---|
| hit@3, expected file in top 3 | 27/28 (96%) |
| hit@3, expected row/section in top 3 | 26/28 (93%) |
| Out-of-scope questions refused | 4/5 (80%) |
| In-scope questions wrongly refused | 1/28 |

| Not yet measured | Command |
|---|---|
| Hybrid retrieval (BM25 + MiniLM) | pending: `pip install sentence-transformers && RETRIEVER=hybrid python evals/run_eval.py` |
| Grounded answers citing the expected file (LLM step) | pending: `OPENAI_API_KEY=... python evals/run_eval.py --generate` |

The misses are the expected kind for keyword retrieval: "interlibrary loan" doesn't match the row labelled "ILL, Rapido (CSU+)", "library website" doesn't match "Web Team", and "reserve a group study room" matches "Course reserves". Hybrid retrieval is meant to fix the first two, but I haven't recorded hybrid numbers yet. The refusal threshold was picked by hand and checked on this same small set, so treat these numbers as a sanity check, not a benchmark.

## Architecture

```
question
   │
   ▼
1. retrieval.py   BM25 over knowledge-base chunks (optionally + MiniLM embeddings)
   │              top-4 chunks, or nothing if no chunk scores high enough
   │                   └─► nothing relevant → "I don't know" + link to Ask a Librarian
   ▼
2. rag.py + llm.py   LLM gets the question and the numbered chunks [1]..[4] and
   │                 must answer only from them, citing [n] after every sentence
   ▼
3. grounding check   drop sentences with no citation or citing a chunk that
   │                 wasn't retrieved; if nothing is left → "I don't know"
   ▼
answer + sources ([1] contacts_help_services.md, ...)
```

| File | Role |
|---|---|
| `retrieval.py` | Chunking, BM25, optional hybrid fusion, index saved under `.index/` |
| `rag.py` | Prompt, grounding check, refusals, the `answer()` entry point |
| `llm.py` | Clients for OpenAI, Anthropic, Gemini and Ollama (standard library HTTPS only) |
| `answer.py` | No-LLM fallback: picks the best-matching line from the retrieved chunks |
| `chatbot_app.py` | Streamlit UI |
| `evals/run_eval.py` | Offline retrieval and refusal eval |
| `knowledge_base/` | The source documents (4 Markdown files) |

## How to run

```bash
pip install -r requirements.txt
streamlit run chatbot_app.py                    # no key: quotes the knowledge base
```

Pick a provider with environment variables. If `LLM_PROVIDER` isn't set, the first provider with a key is used; `LLM_MODEL` overrides the default model.

| Provider | Environment | Default model |
|---|---|---|
| OpenAI | `OPENAI_API_KEY=...` | `gpt-4o-mini` |
| Anthropic | `ANTHROPIC_API_KEY=...` | `claude-haiku-4-5` |
| Gemini | `GEMINI_API_KEY=...` (or `GOOGLE_API_KEY`) | `gemini-2.5-flash` |
| Ollama (local) | `LLM_PROVIDER=ollama` (optional `OLLAMA_HOST`, default `http://localhost:11434`) | `llama3.2` |

```bash
OPENAI_API_KEY=sk-... streamlit run chatbot_app.py
ANTHROPIC_API_KEY=... streamlit run chatbot_app.py
GEMINI_API_KEY=... streamlit run chatbot_app.py
ollama pull llama3.2 && LLM_PROVIDER=ollama streamlit run chatbot_app.py
RETRIEVER=hybrid OPENAI_API_KEY=sk-... streamlit run chatbot_app.py   # + MiniLM embeddings
```

Other settings: `KB_DIR` (knowledge-base folder, default `knowledge_base/`), `INDEX_DIR` (index folder, default `.index/`), `MIN_BM25_SCORE` (default 2.0), `MIN_COSINE` (default 0.45).

To teach it something new, add or edit a Markdown file in `knowledge_base/`; the index rebuilds automatically.

### Docker

```bash
docker build -t sjsu-library-chatbot .
docker run -p 8501:8501 sjsu-library-chatbot                          # quoting mode
docker run -p 8501:8501 -e OPENAI_API_KEY=sk-... sjsu-library-chatbot  # with an LLM
```

Then open http://localhost:8501. The image runs as a non-root user and writes its index to `/tmp/index`.

### Evaluation

```bash
python evals/run_eval.py                         # retrieval + refusals, offline
python evals/run_eval.py --out evals/results.md  # refresh the committed results
python evals/run_eval.py --generate              # also runs the LLM step (needs a key)
```

### Tests and checks

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest --cov                 # fake LLM, no API keys, no downloads
ruff check . && ruff format --check .
mypy
pre-commit install           # optional: run the same checks on every commit
```

The tests cover: answers cite the retrieved chunks and their files, uncited or wrongly cited sentences are dropped, out-of-scope questions are refused without calling the LLM, the no-key fallback quotes the knowledge base, provider selection from the environment, the saved index being reused, hybrid ranking with fake embeddings, and clear errors for a missing knowledge-base folder, a bad threshold value and failed LLM requests. GitHub Actions runs lint, type checking, the tests with coverage, and the retrieval eval on every push.

## Design choices

**Chunking.** Each row of a Markdown table becomes one chunk written out with its column names (e.g. `Service: KLEVR Lab; Who to Contact: Sharon Thompson; ...`), and each heading with its bullet points becomes one chunk. The 4 files give 36 chunks.

**Retrieval.** BM25 by default: pure Python, no model download, and it handles the names and acronyms (KLEVR, Leganto, OneSearch) that most questions here hinge on. `RETRIEVER=hybrid` adds `all-MiniLM-L6-v2` sentence embeddings (`pip install sentence-transformers`) and merges the two rankings with reciprocal rank fusion, which should help with paraphrases ("leave my car" vs "parking"). A question is refused when the best BM25 score is below `MIN_BM25_SCORE` (default 2.0) and, in hybrid mode, the best cosine similarity is also below `MIN_COSINE` (0.45).

**Index.** Chunks (and embeddings in hybrid mode) are saved in `.index/`, keyed by a hash of the knowledge-base files, so they are only rebuilt when a file changes. The Streamlit app also keeps the loaded index in `st.cache_resource`, so it isn't rebuilt on every rerun.

**No LLM configured.** The app still retrieves, then quotes the single best-matching line from the retrieved chunks (`answer.py`) and labels it *Quoted from the knowledge base*. The same fallback is used if an LLM call fails.

**No SDKs.** The API clients in `llm.py` use plain HTTPS requests from the Python standard library, so no provider SDKs are needed; the RAG modules have no third-party dependencies at all.

Earlier versions used LlamaIndex with `response_mode="no_text"`, which only did the retrieval half and rebuilt the index on every page rerun. The knowledge base is a few small files, so retrieval is now done directly in `retrieval.py`.

## Limits

- **The knowledge base is small**: 4 files, and two of them (`event_funding_request.md`, `sjsu_parking_permit_request.md`) are 2-line stubs, so the bot can say the form exists but not how to fill it in. Most real visitor questions (hours, borrowing, printing, rooms) are out of scope and get pointed to [Ask a Librarian](https://library.sjsu.edu/ask-librarian).
- The org chart is a snapshot from June 16, 2025 and only lists key roles.
- The grounding check only verifies that each sentence cites a retrieved chunk; it doesn't verify that the chunk actually supports the sentence.
- The eval set is 33 questions and the refusal threshold was tuned on it.
- Next step: ingest the library's public LibAnswers FAQ and LibGuides (with the library's permission), which would cover the common visitor questions, then grow the eval set to match.

## Web chatbot

`index.html` + `script.js` + `style.css` is a standalone chat page with keyword-matched answers written for library visitors. `embed.html` explains how to add it to a Google Sites page, and `google-sites-embed.html` contains the embed snippet. Alternative page designs (`*-chatbot.html`, `new.html`) are kept in `extras/designs/`.

## Also in this repo

`extras/email/finals_week_template.html` / `.txt` is a reusable email template for Finals Week volunteer and donor outreach. See [extras/email/FINALS_WEEK_TEMPLATE.md](extras/email/FINALS_WEEK_TEMPLATE.md).
