"""AI service functions used by the API views."""

from ai.models import QuizGenerationJob, VideoGenerationJob
from ai.services.quiz_generator import generate_quiz_for_topic


def run_quiz_generation(topic_id: int, user) -> QuizGenerationJob:
    """
    Synchronous quiz generation for now (swap to Celery task later).
    Records a job, generates questions, updates the job, and indexes the topic
    for the RAG chatbot.
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

    # Keep the chatbot index fresh so newly published topics are searchable.
    from ai.services.rag import index_topic

    try:
        index_topic(topic)
    except Exception:  # noqa: BLE001 - indexing must never fail the request
        pass
    return job


def request_video_generation(topic_id: int, user) -> VideoGenerationJob:
    """
    Generates an explainer script for a topic and hands it to the avatar-video
    provider. With a real provider key (e.g. HeyGen) the job is dispatched for
    async rendering; otherwise the job completes with the script so the flow is
    runnable end-to-end offline.
    """
    from academics.models import Topic

    topic = Topic.objects.get(pk=topic_id)
    job = VideoGenerationJob.objects.create(
        tenant=topic.tenant, topic=topic, requested_by=user
    )
    try:
        from ai.providers.avatar import generate_script, render_video

        job.status = VideoGenerationJob.Status.RUNNING
        job.save(update_fields=["status"])
        job.script = generate_script(topic)
        provider = render_video(job)
        job.provider = provider
        job.status = VideoGenerationJob.Status.COMPLETED
        if not job.video_url:
            # No real provider: completed but render awaits a key in production.
            job.video_url = ""
    except Exception as exc:  # noqa: BLE001
        job.status = VideoGenerationJob.Status.FAILED
        job.error = str(exc)
    job.save()

    topic.video_generated = bool(job.provider)
    topic.save(update_fields=["video_generated"])
    return job
