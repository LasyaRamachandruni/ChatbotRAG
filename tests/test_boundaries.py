import io
import urllib.error

import pytest

import llm as llm_module
import retrieval


def test_missing_knowledge_base_folder_gives_clear_error(tmp_path):
    with pytest.raises(FileNotFoundError, match="KB_DIR"):
        retrieval.build_retriever(kb_dir=tmp_path / "nope", index_dir=tmp_path / "idx")


def test_bad_threshold_env_var_gives_clear_error(monkeypatch):
    monkeypatch.setenv("MIN_BM25_SCORE", "high")
    with pytest.raises(ValueError, match="MIN_BM25_SCORE must be a number"):
        retrieval._env_float("MIN_BM25_SCORE", 2.0)
    monkeypatch.setenv("MIN_BM25_SCORE", "")
    assert retrieval._env_float("MIN_BM25_SCORE", 2.0) == 2.0


def test_http_errors_become_llm_errors(monkeypatch):
    def refuse(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 401, "Unauthorized", {}, io.BytesIO(b"bad key"))

    monkeypatch.setattr(llm_module.urllib.request, "urlopen", refuse)
    call = llm_module.openai_llm("gpt-4o-mini", "sk-test")
    with pytest.raises(llm_module.LLMError, match="HTTP 401: bad key"):
        call("system", "user")


def test_unreachable_host_becomes_llm_error(monkeypatch):
    def unreachable(req, timeout):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(llm_module.urllib.request, "urlopen", unreachable)
    call = llm_module.ollama_llm("llama3.2", "http://localhost:1")
    with pytest.raises(llm_module.LLMError, match="Could not reach"):
        call("system", "user")
