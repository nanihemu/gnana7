from rest_framework import generics, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import HasRole, IsTeacher
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
    lookup_field = "pk"

    def get_queryset(self):
        return QuizGenerationJob.objects.all()


class RequestVideoView(APIView):
    """Teacher requests AI avatar-video generation for a topic."""

    permission_classes = [HasRole(["admin", "teacher"])]

    def post(self, request, topic_id):
        job = request_video_generation(topic_id, request.user)
        return Response({"job": job.id, "status": job.status})


class VideoJobDetailView(generics.RetrieveAPIView):
    permission_classes = [HasRole(["admin", "teacher", "student"])]
    lookup_field = "pk"

    def get_queryset(self):
        return VideoGenerationJob.objects.all()


class ChatSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=2000)
    history = serializers.ListField(
        child=serializers.DictField(), required=False, default=list
    )


class ChatView(APIView):
    """RAG chatbot: grounded answer from the school's posted topics + sources."""

    permission_classes = [HasRole(["admin", "teacher", "student", "parent"])]

    def post(self, request):
        from academics.models import Topic

        ser = ChatSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        from ai.services.rag import answer, index_topic

        # Make sure recently posted topics are searchable.
        topics = Topic.objects.all().select_related()
        for topic in topics[:50]:
            index_topic(topic)

        result = answer(
            data["question"],
            topic_qs=topics,
            history=[m for m in data.get("history") or [] if isinstance(m, dict)],
        )
        return Response(result)


class GenerateFeedbackView(APIView):
    """Teacher asks the LLM to draft feedback for a submission (not yet saved)."""

    permission_classes = [IsTeacher]

    def post(self, request, submission_id):
        from academics.models import Submission
        from ai.services.feedback import generate_submission_feedback

        try:
            submission = Submission.objects.get(pk=submission_id)
        except Submission.DoesNotExist:
            return Response({"detail": "Submission not found."}, status=404)
        result = generate_submission_feedback(submission)
        return Response(result)


class IndexMaterialView(APIView):
    """Re-index all topics of the current tenant for the RAG chatbot."""

    permission_classes = [HasRole(["admin", "teacher"])]

    def post(self, request):
        from academics.models import Topic
        from ai.services.rag import index_topic

        topics = Topic.objects.all()
        indexed = sum(1 for t in topics if index_topic(t))
        return Response({"indexed": indexed, "total": topics.count()})