"""Small clients for the LLM providers the chatbot can use.

Pick one with LLM_PROVIDER=openai|anthropic|gemini|ollama. If LLM_PROVIDER is not
set, the first provider with an API key in the environment is used. LLM_MODEL
overrides the default model. With no provider configured, get_llm() returns None
and the chatbot quotes the knowledge base instead of generating an answer.

Only the standard library is used (plain HTTPS requests), so no SDKs are needed.
"""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Callable

# (system prompt, user prompt) -> answer text
LLM = Callable[[str, str], str]

DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-haiku-4-5",
    "gemini": "gemini-2.5-flash",
    "ollama": "llama3.2",
}


def _post(url: str, payload: dict, headers: dict, timeout: float = 60) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def openai_llm(model: str, api_key: str) -> LLM:
    base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")

    def call(system: str, user: str) -> str:
        data = _post(
            f"{base}/chat/completions",
            {"model": model, "temperature": 0,
             "messages": [{"role": "system", "content": system},
                          {"role": "user", "content": user}]},
            {"Authorization": f"Bearer {api_key}"},
        )
        return data["choices"][0]["message"]["content"]

    return call


def anthropic_llm(model: str, api_key: str) -> LLM:
    def call(system: str, user: str) -> str:
        data = _post(
            "https://api.anthropic.com/v1/messages",
            {"model": model, "max_tokens": 400, "temperature": 0, "system": system,
             "messages": [{"role": "user", "content": user}]},
            {"x-api-key": api_key, "anthropic-version": "2023-06-01"},
        )
        return "".join(b.get("text", "") for b in data["content"])

    return call


def gemini_llm(model: str, api_key: str) -> LLM:
    def call(system: str, user: str) -> str:
        data = _post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            {"systemInstruction": {"parts": [{"text": system}]},
             "contents": [{"role": "user", "parts": [{"text": user}]}],
             "generationConfig": {"temperature": 0}},
            {"x-goog-api-key": api_key},
        )
        return "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"])

    return call


def ollama_llm(model: str, host: str) -> LLM:
    def call(system: str, user: str) -> str:
        data = _post(
            f"{host.rstrip('/')}/api/chat",
            {"model": model, "stream": False, "options": {"temperature": 0},
             "messages": [{"role": "system", "content": system},
                          {"role": "user", "content": user}]},
            {},
            timeout=180,
        )
        return data["message"]["content"]

    return call


def get_llm() -> tuple[str, LLM] | None:
    """Return (description, llm) for the configured provider, or None."""
    env = os.environ
    keys = {
        "openai": env.get("OPENAI_API_KEY"),
        "anthropic": env.get("ANTHROPIC_API_KEY"),
        "gemini": env.get("GEMINI_API_KEY") or env.get("GOOGLE_API_KEY"),
        "ollama": env.get("OLLAMA_HOST"),
    }
    provider = env.get("LLM_PROVIDER", "").lower()
    if not provider:
        provider = next((p for p, k in keys.items() if k), "")
    if not provider:
        return None
    if provider not in DEFAULT_MODELS:
        raise ValueError(f"Unknown LLM_PROVIDER {provider!r}; use one of {', '.join(DEFAULT_MODELS)}")

    model = env.get("LLM_MODEL") or DEFAULT_MODELS[provider]
    if provider == "ollama":
        return f"ollama/{model}", ollama_llm(model, keys["ollama"] or "http://localhost:11434")
    if not keys[provider]:
        return None  # provider chosen but no key: fall back to quoting
    factory = {"openai": openai_llm, "anthropic": anthropic_llm, "gemini": gemini_llm}[provider]
    return f"{provider}/{model}", factory(model, keys[provider])
