"""
AI-assisted feedback on student submissions.

Given a submission's answers and the assessment's correct answers, the LLM
drafts constructive, age-appropriate feedback per question and a short overall
note. When no LLM is configured it falls back to a deterministic summary that
points out correct vs. incorrect questions.
"""

import json

from academics.models import Question, Submission

from .llm import chat_text, extract_json_array


def _build_exchange(submission: Submission) -> list[dict]:
    """Question + student answer + correct answer rows for the LLM."""
    questions = list(
        Question.objects.filter(assessment=submission.assessment).order_by("id")
    )
    answers = submission.answers or {}
    rows = []
    for q in questions:
        chosen = answers.get(str(q.id), answers.get(q.id))
        correct = q.options[q.correct_index] if (q.q_type == "mcq" and q.correct_index is not None and q.options) else None
        student_answer = (
            q.options[chosen]
            if isinstance(chosen, int) and q.options and 0 <= chosen < len(q.options)
            else chosen
        )
        rows.append(
            {
                "question": q.text,
                "student_answer": student_answer if student_answer is not None else "(not answered)",
                "correct_answer": correct or "(see teacher)",
                "marks": q.marks,
            }
        )
    return rows


def _llm_feedback(rows: list[dict], assessment_title: str) -> dict:
    system = (
        "You are a supportive school teacher. Write feedback a student can learn "
        "from. Praise what's right, gently explain what's wrong, and suggest one "
        "concrete next step. Keep every item to 1-3 sentences."
    )
    prompt = (
        "Here is a student's submission for the assessment "
        f'"{assessment_title}". '
        'For each question produce a JSON object with keys "question", "comment". '
        'Then include a final object with "question": "OVERALL", '
        '"comment": <one short paragraph>.\n\n'
        "Questions:\n" + json.dumps(rows, indent=2)
    )
    content = chat_text(prompt, system=system, temperature=0.4)
    if not content:
        return _template_feedback(rows)
    try:
        items = extract_json_array(content)
        per_question = [
            {"question": it.get("question", ""), "comment": it.get("comment", "")}
            for it in items
        ]
        overall = next(
            (it["comment"] for it in per_question if it["question"] == "OVERALL"),
            "",
        )
        per_question = [it for it in per_question if it["question"] != "OVERALL"]
        return {"content": overall, "per_question": per_question, "is_ai_assisted": True}
    except Exception:  # noqa: BLE001 - never fail feedback on bad LLM output
        return _template_feedback(rows)


def _template_feedback(rows: list[dict]) -> dict:
    answered = [r for r in rows if r["student_answer"] != "(not answered)"]
    correct = [r for r in rows if r["student_answer"] == r["correct_answer"]]
    wrong = [r for r in rows if r["student_answer"] != r["correct_answer"] and r["student_answer"] != "(not answered)"]
    if not answered:
        overall = "No answers were recorded for this submission."
    elif not wrong:
        overall = f"Great work — you got all {len(correct)} questions right. Keep it up!"
    else:
        overall = (
            f"You answered {len(correct)} of {len(answered)} correctly. "
            f"Revisit: {', '.join(r['question'][:40] for r in wrong[:3])}."
        )
    per_question = [
        {
            "question": r["question"],
            "comment": (
                "Correct — well done."
                if r["student_answer"] == r["correct_answer"]
                else "Not quite — review this one; ask your teacher if stuck."
                if r["student_answer"] != "(not answered)"
                else "Not answered."
            ),
        }
        for r in rows
    ]
    return {"content": overall, "per_question": per_question, "is_ai_assisted": False}


def generate_submission_feedback(submission: Submission) -> dict:
    """Draft feedback for a submission (does not persist)."""
    rows = _build_exchange(submission)
    if rows and (submission.answers or {}):
        return _llm_feedback(rows, submission.assessment.title)
    return _template_feedback(rows)
