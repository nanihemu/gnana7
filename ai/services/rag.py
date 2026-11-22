"""
Retrieval-augmented generation for the SMS.

Topics (title + description) are embedded into a `TopicEmbedding` row per topic.
A user question is embedded and compared by cosine similarity (pure Python —
no numpy / vector-DB dependency at this scale). The top-k matching chunks are
fed to the LLM as grounded context so answers come from the school's material.
"""

import hashlib
import math
import re

from ai.models import TopicEmbedding

from .llm import chat_text, embed


def _cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two float vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def topic_text(topic) -> str:
    """The text we embed for a topic (title + description)."""
    return f"{topic.title}\n{topic.description or ''}".strip()


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def index_topic(topic) -> bool:
    """
    Embed a topic if its content changed. Returns True if (re)indexed.
    """
    text = topic_text(topic)
    digest = _hash(text)
    emb, _ = TopicEmbedding.objects.get_or_create(
        tenant=topic.tenant, topic=topic, defaults={"vector": []}
    )
    if emb.content_hash == digest and emb.vector:
        return False

    vector = embed(text)
    if not vector:
        return False

    emb.content = text
    emb.content_hash = digest
    emb.vector = vector
    emb.save()
    return True


def search(query: str, topic_qs, k: int = 4) -> list[dict]:
    """
    Return the top-k topics for a query as dicts: {id, title, score}.
    topic_qs should already be tenant-scoped (TenantManager does this).
    """
    query_vector = embed(query)
    if not query_vector:
        # No provider — fall back to naive keyword matching so the endpoint
        # still returns something grounded in the tenant's material.
        return _keyword_search(query, topic_qs, k)

    rows = (
        TopicEmbedding.objects.filter(topic_id__in=topic_qs.values_list("id", flat=True))
        .select_related("topic")
        .only("vector", "topic_id")
    )
    scored = []
    for row in rows:
        if not row.vector:
            continue
        sim = _cosine(query_vector, row.vector)
        if sim > 0:
            scored.append((sim, row.topic))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {"id": topic.id, "title": topic.title, "score": round(sim, 4)}
        for sim, topic in scored[:k]
    ]


def _keyword_search(query: str, topic_qs, k: int = 4) -> list[dict]:
    """Cheap deterministic fallback: term overlap with topic title/description."""
    terms = {re.sub(r"[^a-z0-9]+", "", t.lower()) for t in query.split()}
    terms = {t for t in terms if len(t) > 2}
    scored = []
    for topic in topic_qs:
        if not terms:
            continue
        haystack = f"{topic.title} {topic.description or ''}".lower()
        hits = sum(1 for term in terms if term in haystack)
        if hits:
            scored.append((hits, topic))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [{"id": t.id, "title": t.title, "score": round(hits, 4)} for hits, t in scored[:k]]


def answer(question: str, topic_qs, history: list = None, k: int = 4) -> dict:
    """
    Embed the question, retrieve top-k topics, and answer with an LLM grounded
    in them. Returns {answer, sources}. When no provider is configured, returns
    an answer assembled from the retrieved topic snippets.
    """
    hits = search(question, topic_qs, k)
    sources = hits

    if not hits:
        fallback = (
            "I couldn't find material about that in your school's content yet. "
            "Try asking about a specific subject or a topic your teacher has posted."
        )
        return {"answer": fallback, "sources": [], "grounded": False}

    topic_map = {t.id: t for t in topic_qs.filter(id__in=[h["id"] for h in hits])}
    context = "\n\n".join(
        f"TOPIC: {topic_map[h['id']].title}\n{topic_map[h['id']].description or ''}"
        for h in hits
        if h["id"] in topic_map
    )

    system = (
        "You are the SMS learning assistant for a school. Answer the student's "
        "question using ONLY the school material provided below. Be concise and "
        "age-appropriate. If the material doesn't answer the question, say so "
        "and suggest rephrasing. Do not invent facts outside the material."
    )

    history_text = ""
    if history:
        lines = [f"{m.get('role')}: {m.get('content')}" for m in history[-6:]]
        history_text = "Chat history (older first):\n" + "\n".join(lines) + "\n\n"

    prompt = (
        f"{history_text}"
        f"School material:\n{context}\n\n"
        f"Student question: {question}\n\n"
        "Answer:"
    )

    reply = chat_text(prompt, system=system)
    if reply is None:
        # No LLM — deterministic response from retrieved snippets.
        titles = " • ".join(h["title"] for h in hits)
        reply = (
            f"Here's what we found about that in your school's material: {titles}. "
            "Connect these topics to your lessons or ask your teacher to expand them."
        )
        return {"answer": reply, "sources": sources, "grounded": True}

    return {"answer": reply, "sources": sources, "grounded": True}
