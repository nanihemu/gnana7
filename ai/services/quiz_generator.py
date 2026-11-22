"""
Quiz generation service.

This module is provider-agnostic: it exposes a `generate_quiz_for_topic` function
that the API view calls. When OPENAI_API_KEY is set it calls a real LLM; otherwise
it falls back to a deterministic template generator so the whole system stays
runnable and testable without credentials.
"""

import json
import os
import random

from academics.models import Question, Topic


def _template_questions(topic: Topic, n: int = 5) -> list[dict]:
    """Deterministic fallback: builds simple MCQs from the topic title."""
    base = topic.title or "this topic"
    questions = []
    for i in range(n):
        questions.append(
            {
                "text": f"Which of the following best relates to {base}? (question {i + 1})",
                "q_type": "mcq",
                "options": [
                    f"Option A about {base}",
                    f"Option B about {base}",
                    f"Option C about {base}",
                    f"Option D about {base}",
                ],
                "correct_index": i % 4,
                "marks": 1,
            }
        )
    return questions


def _llm_questions(topic: Topic, n: int = 5) -> list[dict]:
    """Call an LLM (OpenAI-compatible) to generate curriculum-aligned questions."""
    import openai

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = (
        "You are a quiz generator for students. Based on the topic below, generate "
        f"{n} multiple-choice questions (MCQ). "
        "Return ONLY valid JSON, an array of objects with keys: "
        "text, options (array of 4 strings), correct_index (int 0-3), marks (int).\n\n"
        f"Topic title: {topic.title}\nTopic description:\n{topic.description or 'N/A'}"
    )
    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    content = resp.choices[0].message.content
    start = content.find("[")
    end = content.rfind("]")
    return json.loads(content[start : end + 1])


def generate_quiz_for_topic(topic: Topic, n: int = 5) -> list[Question]:
    """Generate questions for a topic and persist them. Idempotent per topic."""
    if Question.objects.filter(topic=topic).exists():
        # Already generated — return existing (caching behavior).
        return list(Question.objects.filter(topic=topic))

    try:
        if os.getenv("OPENAI_API_KEY"):
            data = _llm_questions(topic, n)
        else:
            data = _template_questions(topic, n)
    except Exception as exc:  # noqa: BLE001 - degrade gracefully on provider errors
        # Fall back to templates so the pipeline never hard-fails.
        data = _template_questions(topic, n)

    created = []
    for q in data:
        question = Question.objects.create(
            tenant=topic.tenant,
            topic=topic,
            text=q["text"],
            q_type=q.get("q_type", "mcq"),
            options=q.get("options", []),
            correct_index=q.get("correct_index"),
            marks=q.get("marks", 1),
        )
        created.append(question)

    topic.quiz_generated = True
    topic.save(update_fields=["quiz_generated"])
    return created