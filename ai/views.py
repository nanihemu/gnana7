from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import HasRole
from .models import QuizGenerationJob, VideoGenerationJob
from .services import request_video_generation, run_quiz_generation


class GenerateQuizView(APIView):
    """Teacher triggers AI quiz generation for a topic. Returns the job + created questions."""

    permission_classes = [HasRole(["admin", "teacher"])]

    def post(self, request, topic_id):
        job = run_quiz_generation(topic_id, request.user)
        return Response(
            {
                "job": job.id,
                "status": job.status,
                "questions_created": job.questions_created,
                "error": job.error or None,
            }
        )


class QuizJobDetailView(generics.RetrieveAPIView):
    permission_classes = [HasRole(["admin", "teacher", "student"])]
    queryset = QuizGenerationJob.objects.all()
    lookup_field = "pk"


class RequestVideoView(APIView):
    """Teacher requests AI avatar-video generation for a topic."""

    permission_classes = [HasRole(["admin", "teacher"])]

    def post(self, request, topic_id):
        job = request_video_generation(topic_id, request.user)
        return Response({"job": job.id, "status": job.status})


class VideoJobDetailView(generics.RetrieveAPIView):
    permission_classes = [HasRole(["admin", "teacher", "student"])]
    queryset = VideoGenerationJob.objects.all()
    lookup_field = "pk"