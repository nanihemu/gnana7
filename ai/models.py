from django.db import models

from core.managers import TenantModel


class QuizGenerationJob(TenantModel):
    """Tracks an AI quiz-generation request so clients can poll for completion."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    topic = models.ForeignKey(
        "academics.Topic", on_delete=models.CASCADE, related_name="quiz_jobs"
    )
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    requested_by = models.ForeignKey("core.User", on_delete=models.SET_NULL, null=True)
    questions_created = models.PositiveIntegerField(default=0)
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_quiz_jobs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Quiz job for #{self.topic_id} · {self.status}"


class VideoGenerationJob(TenantModel):
    """Tracks an AI avatar-video generation request (async, provider-backed)."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    topic = models.ForeignKey(
        "academics.Topic", on_delete=models.CASCADE, related_name="video_jobs"
    )
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    requested_by = models.ForeignKey("core.User", on_delete=models.SET_NULL, null=True)
    script = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    provider = models.CharField(
        max_length=50, blank=True,
        help_text="Which provider handled this job: heygen / fallback",
    )
    provider_meta = models.JSONField(default=dict, blank=True)
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_video_jobs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Video job for #{self.topic_id} · {self.status}"


class TopicEmbedding(TenantModel):
    """
    Stored embedding for a Topic so the RAG chatbot can search school material
    without a vector database. A JSONField plus pure-Python cosine similarity is
    plenty for a school-sized corpus; swap for pgvector if it ever grows.
    """

    topic = models.OneToOneField(
        "academics.Topic", on_delete=models.CASCADE, related_name="embedding"
    )
    content = models.TextField(blank=True, help_text="Text that was embedded")
    content_hash = models.CharField(max_length=64, blank=True)
    vector = models.JSONField(default=list, help_text="Embedding float array")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_topic_embeddings"

    def __str__(self):
        return f"Embedding for #{self.topic_id}"