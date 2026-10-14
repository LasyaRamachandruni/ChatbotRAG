FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    INDEX_DIR=/tmp/index

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY answer.py llm.py rag.py retrieval.py chatbot_app.py ./
COPY knowledge_base ./knowledge_base

RUN useradd --create-home --uid 1000 app
USER app

EXPOSE 8501
# Pass a provider key at run time, e.g. docker run -e OPENAI_API_KEY=... ; none = quoting mode.
CMD ["streamlit", "run", "chatbot_app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
