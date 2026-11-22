"""AI service functions used by the API views."""

from ai.models import QuizGenerationJob, VideoGenerationJob
from ai.services.quiz_generator import generate_quiz_for_topic


def run_quiz_generation(topic_id: int, user) -> QuizGenerationJob:
    """
    Synchronous quiz generation for now (swap to Celery task later).
    Creates a job record, generates questions, updates the job.
    """
    from academics.models import Topic

    topic = Topic.objects.get(pk=topic_id)
    job = QuizGenerationJob.objects.create(
        tenant=topic.tenant, topic=topic, requested_by=user
    )
    try:
        job.status = QuizGenerationJob.Status.RUNNING
        job.save(update_fields=["status"])
        questions = generate_quiz_for_topic(topic)
        job.questions_created = len(questions)
        job.status = QuizGenerationJob.Status.COMPLETED
    except Exception as exc:  # noqa: BLE001
        job.status = QuizGenerationJob.Status.FAILED
        job.error = str(exc)
    job.save()
    return job


def request_video_generation(topic_id: int, user) -> VideoGenerationJob:
    """
    Queues a video-generation job. Currently records the job; the actual
    TTS + avatar render is async and provider-backed (see ai/providers/).
    """
    from academics.models import Topic

    topic = Topic.objects.get(pk=topic_id)
    job = VideoGenerationJob.objects.create(
        tenant=topic.tenant, topic=topic, requested_by=user
    )
    # In production this dispatches to Celery: queue_video_generation.delay(job.id)
    return job