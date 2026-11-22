from django.contrib import admin

from .models import QuizGenerationJob, TopicEmbedding, VideoGenerationJob


@admin.register(QuizGenerationJob)
class QuizGenerationJobAdmin(admin.ModelAdmin):
    list_display = ("topic", "status", "questions_created", "created_at")
    list_filter = ("status",)


@admin.register(VideoGenerationJob)
class VideoGenerationJobAdmin(admin.ModelAdmin):
    list_display = ("topic", "status", "provider", "created_at")
    list_filter = ("status", "provider")


@admin.register(TopicEmbedding)
class TopicEmbeddingAdmin(admin.ModelAdmin):
    list_display = ("topic", "updated_at")
