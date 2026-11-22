"""
Central LLM / embedding client.

The whole AI subsystem talks to an OpenAI-compatible API (a real provider or a
proxy). This module reads connection settings once and exposes small helpers so
no other module has to construct clients or hard-code model names. When no key
is configured everything degrades gracefully (callers keep their fallbacks).
"""

import json
import os
import re

DEFAULT_CHAT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
DEFAULT_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")


def get_client():
    """Build an OpenAI-compatible client from env, or None if not configured."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    import openai

    kwargs = {"api_key": api_key}
    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        kwargs["base_url"] = base_url
    return openai.OpenAI(**kwargs)


def strip_code_fences(content: str) -> str:
    """Remove ```json / ``` fences that LLMs love to wrap JSON in."""
    if not content:
        return content or ""
    fence = re.search(r"```(?:json)?\s*(.*?)\s*```", content, re.DOTALL)
    if fence:
        return fence.group(1).strip()
    return content.strip()


def extract_json_array(content: str):
    """Parse the first JSON array found in an LLM response."""
    text = strip_code_fences(content)
    start = text.find("[")
    if start == -1:
        raise ValueError("No JSON array found in LLM response")
    end = text.rfind("]")
    return json.loads(text[start : end + 1])


def chat(messages, model: str | None = None, temperature: float = 0.5) -> str | None:
    """Single completion; returns the assistant message or None when unconfigured."""
    client = get_client()
    if client is None:
        return None
    resp = client.chat.completions.create(
        model=model or DEFAULT_CHAT_MODEL,
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content


def chat_text(prompt: str, system: str | None = None, model: str | None = None, temperature: float = 0.5) -> str | None:
    """Convenience: one user prompt (+ optional system) → assistant text."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return chat(messages, model=model, temperature=temperature)


def embed(text: str) -> list[float] | None:
    """Embed a single string; returns a float list or None when unconfigured."""
    client = get_client()
    if client is None:
        return None
    resp = client.embeddings.create(model=DEFAULT_EMBEDDING_MODEL, input=text)
    return resp.data[0].embedding


def embed_many(texts: list[str]) -> list[list[float]]:
    """Embed many strings in one call; returns [] when unconfigured."""
    client = get_client()
    if client is None:
        return []
    resp = client.embeddings.create(model=DEFAULT_EMBEDDING_MODEL, input=texts)
    ordered = sorted(resp.data, key=lambda d: d.index)
    return [d.embedding for d in ordered]
