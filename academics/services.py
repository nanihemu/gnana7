"""Grading helpers for submissions (auto-grading + teacher grading)."""

from .models import Question, Submission


def auto_grade(submission: Submission) -> Submission:
    """
    Grade every MCQ in the assessment by comparing the student's chosen option
    index against the question's correct index. Sets score (out of the sum of
    marks for answered/graded questions) and marks the submission graded when
    every question is auto-gradeable. Also syncs the assessment's total_marks.
    """
    questions = list(
        Question.objects.filter(assessment=submission.assessment).order_by("id")
    )
    if not questions:
        return submission

    # Keep the assessment's declared total in sync with its question bank so
    # downstream analytics compute correct percentages.
    total_marks = sum(q.marks for q in questions)
    if submission.assessment.total_marks != total_marks:
        submission.assessment.total_marks = total_marks
        submission.assessment.save(update_fields=["total_marks"])

    answers = submission.answers or {}
    total = 0
    earned = 0.0
    all_graded = True
    for q in questions:
        total += q.marks
        chosen = answers.get(str(q.id), answers.get(q.id))
        if q.q_type == "mcq" and q.correct_index is not None and q.options:
            try:
                idx = int(chosen) if chosen is not None else None
            except (TypeError, ValueError):
                idx = None
            if idx is not None and 0 <= idx < len(q.options):
                if idx == q.correct_index:
                    earned += q.marks
            else:
                all_graded = False
        else:
            # Free-text questions can't be auto-graded.
            all_graded = False

    if total:
        submission.score = round(earned, 2)
    submission.is_graded = all_graded
    submission.save()
    return submission


def teacher_grade(submission: Submission, score: float) -> Submission:
    """Record a teacher-assigned score for a submission."""
    submission.score = round(float(score), 2)
    submission.is_graded = True
    submission.save()
    return submission
