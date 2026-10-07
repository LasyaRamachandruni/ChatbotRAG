# SJSU King Library Chatbot

Chatbots that answer common questions about the Dr. Martin Luther King, Jr. Library at San José State University: staff and departments, who to contact for help, and internal forms such as parking permits and event funding.

There are two versions:

| Version | How it answers | Runs where |
|---|---|---|
| **Retrieval chatbot** (`chatbot_app.py`) | Searches a Markdown knowledge base with sentence embeddings and returns the best-matching line | Python / Streamlit, fully local, no API key |
| **Web chatbot** (`index.html`, `script.js`) | Rule-based answers written for library visitors | Any browser; embeddable in Google Sites |

## Retrieval chatbot

```
question ──► embed (all-MiniLM-L6-v2) ──► vector search over knowledge_base/*.md
                                              │
                          most similar sections ▼
                           answer.py picks the single best line ──► reply
```

1. The Markdown files in `knowledge_base/` are indexed with LlamaIndex and a local Hugging Face embedding model.
2. A question retrieves the most similar sections.
3. `answer.py` picks the line that shares the most words with the question, giving extra weight to the section it sits in. For example, *"Who is the dean?"* returns *"Dean: Michael Meth"* from the Dean's Office section.

No text is generated, so answers always come word for word from the knowledge base, and no LLM or API key is needed.

```bash
pip install -r requirements.txt
streamlit run chatbot_app.py
```

To teach it something new, add or edit a Markdown file in `knowledge_base/`.

Tests (no model download needed):

```bash
pip install pytest
pytest
```

## Web chatbot

`index.html` + `script.js` + `style.css` is a standalone chat page. `embed.html` explains how to add it to a Google Sites page, and `google-sites-embed.html` contains the embed snippet. Alternative page designs (`*-chatbot.html`, `new.html`) are kept in `extras/designs/`.

## Also in this repo

`extras/email/finals_week_template.html` / `.txt` is a reusable email template for Finals Week volunteer and donor outreach. See [extras/email/FINALS_WEEK_TEMPLATE.md](extras/email/FINALS_WEEK_TEMPLATE.md).
