"""
Quiz generation service.

Provider-agnostic: exposes `generate_quiz_for_topic`, which the API view calls.
When an OpenAI-compatible provider is configured (OPENAI_API_KEY) it calls a real
LLM; otherwise it falls back to deterministic templates so the whole system stays
runnable and testable offline.
"""

import random

from academics.models import Question, Topic

from .llm import chat_text, extract_json_array


def _template_questions(topic: Topic, n: int = 5) -> list[dict]:
    """Deterministic fallback: builds simple MCQs from the topic title."""
    base = topic.title or "this topic"
    questions = []
    for i in range(n):
        options = [
            f"Option A about {base}",
            f"Option B about {base}",
            f"Option C about {base}",
            f"Option D about {base}",
        ]
        correct_index = i % 4
        questions.append(
            {
                "text": f"Which of the following best relates to {base}? (question {i + 1})",
                "q_type": "mcq",
                "options": options,
                "correct_index": correct_index,
                "marks": 1,
            }
        )
    return questions


def _llm_questions(topic: Topic, n: int = 5) -> list[dict]:
    """Ask an LLM for curriculum-aligned MCQs about the topic."""
    prompt = (
        "You are a quiz generator for school students. Based on the topic below, "
        f"generate exactly {n} multiple-choice questions (MCQ). "
        "Each question is a JSON object with keys: "
        '"text" (string), "options" (list of 4 strings), '
        '"correct_index" (int 0-3), "marks" (int, usually 1). '
        "Return ONLY a JSON array of question objects, no extra text.\n\n"
        f"Topic title: {topic.title}\n"
        f"Topic description:\n{topic.description or 'N/A'}"
    )
    content = chat_text(prompt, temperature=0.7)
    if not content:
        raise RuntimeError("LLM returned no content")
    data = extract_json_array(content)
    if not isinstance(data, list):
        raise ValueError("LLM did not return a JSON array")
    return data


def generate_quiz_for_topic(topic: Topic, n: int = 5) -> list[Question]:
    """Generate questions for a topic and persist them. Idempotent per topic."""
    if Question.objects.filter(topic=topic).exists():
        # Already generated — return existing (caching behavior).
        return list(Question.objects.filter(topic=topic))

    try:
        data = _llm_questions(topic, n)
    except Exception:  # noqa: BLE001 - degrade gracefully on provider errors
        data = None

    if not data:
        data = _template_questions(topic, n)

    created = []
    for q in data:
        question = Question.objects.create(
            tenant=topic.tenant,
            topic=topic,
            text=q["text"],
            q_type=q.get("q_type", "mcq"),
            options=q.get("options", [])[:4] or [""] * 4,
            correct_index=q.get("correct_index"),
            marks=q.get("marks", 1),
        )
        created.append(question)

    topic.quiz_generated = True
    topic.save(update_fields=["quiz_generated"])
    return created
