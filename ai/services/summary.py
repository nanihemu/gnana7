"""
Natural-language parent progress summaries.

Turns a child's subject-wise performance data into a short, encouraging
paragraph for parents — strong/weak subjects, quick trend, one suggested next
step. Falls back to a deterministic summary when no LLM is configured.
"""

from .llm import chat_text


def _frames(subjects: list[dict]) -> tuple[list[str], list[str]]:
    strong = [s["subject"] for s in subjects if s["status"] == "strong"]
    weak = [s["subject"] for s in subjects if s["status"] == "weak"]
    return strong, weak


def _llm_summary(child_name: str, subjects: list[dict]) -> str:
    system = (
        "You write warm, concise progress notes for parents, from a teacher's "
        "perspective. 2-4 sentences. Mention strong areas, areas needing "
        "attention, and one concrete next step. No jargon."
    )
    prompt = (
        f"Student: {child_name}\n"
        "Performance per subject (percentage and status):\n"
        + "\n".join(
            f"- {s['subject']}: {s['percentage']}% ({s['status']})"
            for s in subjects
        )
        + "\n\nWrite the progress note:"
    )
    try:
        text = chat_text(prompt, system=system, temperature=0.5)
        if text and text.strip():
            return text.strip()
    except Exception:  # noqa: BLE001 - deterministic summary is the fallback
        pass
    return _template_summary(child_name, subjects)


def _template_summary(child_name: str, subjects: list[dict]) -> str:
    if not subjects:
        return (
            f"{child_name} has no graded assessments yet — performance data "
            "will appear here once submissions are graded."
        )
    strong, weak = _frames(subjects)
    parts = []
    if strong:
        parts.append(f"performing well in {', '.join(strong)}")
    if weak:
        parts.append(f"needs extra support in {', '.join(weak)}")
    if parts:
        msg = f"{child_name} is {parts[0]}" + (
            f" and {parts[1]}." if len(parts) > 1 else "."
        )
    else:
        msg = f"{child_name}'s performance is building steadily across subjects."
    if weak:
        msg += " A little daily practice in those subjects would help a lot."
    return msg


def parent_progress_summary(child_name: str, subjects: list[dict]) -> str:
    """Natural-language summary of a child's performance for parents."""
    if not subjects:
        return _template_summary(child_name, subjects)
    return _llm_summary(child_name, subjects)
