from unittest import mock

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import Tenant, User
from academics.models import Question, SchoolClass, Subject, Topic

from .models import QuizGenerationJob, TopicEmbedding, VideoGenerationJob


class BaseAITest(TestCase):
    def setUp(self):
        # Isolate AI tests from any real provider configured in the shell env.
        self._env = mock.patch.dict(
            "os.environ",
            {"OPENAI_API_KEY": "", "HEYGEN_API_KEY": ""},
            clear=False,
        )
        self._env.start()
        self.addCleanup(self._env.stop)
        self.client = APIClient()
        self.tenant = Tenant.objects.create(name="T1", slug="t1")
        self.teacher = User.objects.create_user(
            username="t1", password="pass12345",
            role=User.RoleChoice.TEACHER, tenant=self.tenant,
        )
        self.student = User.objects.create_user(
            username="s1", password="pass12345",
            role=User.RoleChoice.STUDENT, tenant=self.tenant,
        )
        self.school_class = SchoolClass.objects.create(tenant=self.tenant, name="6")
        self.subject = Subject.objects.create(tenant=self.tenant, name="Science")
        self.topic = Topic.objects.create(
            tenant=self.tenant, teacher=self.teacher,
            subject=self.subject, school_class=self.school_class,
            title="Photosynthesis", description="Plants make food from light.",
        )

    def auth(self, user):
        token = self.client.post(
            reverse("core:token_obtain"),
            {"username": user.username, "password": "pass12345"},
            content_type="application/json",
        ).json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return self.client


class QuizGenerationTests(BaseAITest):
    def test_generates_template_quiz_without_provider(self):
        # No OPENAI_API_KEY in tests (setUp clears it) → deterministic template.
        self.auth(self.teacher)
        resp = self.client.post(f"/api/v1/quiz/generate/{self.topic.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "completed")
        self.assertGreaterEqual(resp.json()["questions_created"], 1)
        self.assertTrue(Question.objects.filter(topic=self.topic).exists())

    def test_generate_is_idempotent(self):
        self.auth(self.teacher)
        self.client.post(f"/api/v1/quiz/generate/{self.topic.id}/")
        self.client.post(f"/api/v1/quiz/generate/{self.topic.id}/")
        self.assertEqual(Question.objects.filter(topic=self.topic).count(), 5)

    def test_topic_indexing_via_service(self):
        from ai.services.rag import index_topic

        indexed = index_topic(self.topic)
        # No embedding provider in tests → not indexed (vector empty), returns False.
        self.assertFalse(indexed)


class VideoGenerationTests(BaseAITest):
    def test_creates_completed_job_with_fallback(self):
        from ai.services import request_video_generation

        job = request_video_generation(self.topic.id, self.teacher)
        self.assertEqual(job.status, VideoGenerationJob.Status.COMPLETED)
        self.assertEqual(job.provider, "fallback")
        self.assertTrue(job.script)  # script always populated via generate_script

    def test_heygen_selected_when_key_set(self):
        from ai.providers import avatar

        job = VideoGenerationJob.objects.create(
            tenant=self.tenant, topic=self.topic, requested_by=self.teacher
        )
        with mock.patch.dict("os.environ", {"HEYGEN_API_KEY": "test-key"}, clear=False):
            with mock.patch.object(avatar, "_heygen_render", return_value=""):
                provider = avatar.render_video(job)
        self.assertEqual(provider, "heygen")


class RAGTests(BaseAITest):
    def test_keyword_fallback_search(self):
        from ai.services.rag import search

        hits = search("photosynthesis plants", Topic.objects.all(), k=3)
        self.assertTrue(hits)
        self.assertEqual(hits[0]["id"], self.topic.id)

    def test_cosine_similarity_helper(self):
        from ai.services.rag import _cosine

        self.assertAlmostEqual(_cosine([1, 0], [1, 0]), 1.0)
        self.assertAlmostEqual(_cosine([1, 0], [0, 1]), 0.0)
        self.assertEqual(_cosine([], [1]), 0.0)

    def test_chat_returns_grounded_answer_without_provider(self):
        self.auth(self.student)
        resp = self.client.post(
            "/api/v1/chat/",
            {"question": "What is photosynthesis?", "history": []},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["answer"])
        self.assertTrue(body["sources"])


class FeedbackTests(BaseAITest):
    def test_template_feedback_fallback(self):
        from ai.services.feedback import generate_submission_feedback
        from academics.models import Assessment, Question, Submission

        assessment = Assessment.objects.create(
            tenant=self.tenant, teacher=self.teacher, subject=self.subject,
            school_class=self.school_class, title="Q",
        )
        q = Question.objects.create(
            tenant=self.tenant, assessment=assessment, text="X?",
            q_type="mcq", options=["a", "b"], correct_index=1, marks=1,
        )
        sub = Submission.objects.create(
            tenant=self.tenant, assessment=assessment, student=self.student,
            answers={str(q.id): 1},
        )
        result = generate_submission_feedback(sub)
        self.assertIn("per_question", result)
        self.assertEqual(result["is_ai_assisted"], False)

    def test_feedback_endpoint_permission(self):
        self.auth(self.student)
        resp = self.client.post("/api/v1/feedback/1/", content_type="application/json")
        self.assertEqual(resp.status_code, 403)


class IndexEndpointTests(BaseAITest):
    def test_admin_can_index(self):
        self.auth(self.teacher)
        resp = self.client.post("/api/v1/index/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("total", resp.json())
