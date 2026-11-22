from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import Tenant, User
from .models import (
    Achievement,
    Assessment,
    Enrollment,
    Notification,
    Question,
    SchoolClass,
    Subject,
    Submission,
    TeacherSubjectAssignment,
    Topic,
)


class BaseSchoolTest(TestCase):
    """Common fixtures: a tenant, admin/teacher/student/parent, class, subject."""

    def setUp(self):
        self.client = APIClient()
        self.tenant = Tenant.objects.create(name="Test School", slug="test-school")
        self.school_class = SchoolClass.objects.create(tenant=self.tenant, name="6", section="A")
        self.subject = Subject.objects.create(tenant=self.tenant, name="Science")

        def make_user(username, role, **kw):
            u = User.objects.create_user(
                username=username, password="pass12345", role=role, tenant=self.tenant
            )
            for k, v in kw.items():
                setattr(u, k, v)
            u.save()
            return u

        self.admin = make_user("admin1", User.RoleChoice.ADMIN)
        self.teacher = make_user("teacher1", User.RoleChoice.TEACHER)
        self.student = make_user("student1", User.RoleChoice.STUDENT)
        self.parent = make_user("parent1", User.RoleChoice.PARENT)

        self.topic = Topic.objects.create(
            tenant=self.tenant,
            teacher=self.teacher,
            subject=self.subject,
            school_class=self.school_class,
            title="Photosynthesis",
        )
        Enrollment.objects.create(
            tenant=self.tenant,
            student=self.student,
            school_class=self.school_class,
            guardian=self.parent,
        )
        self.assessment = Assessment.objects.create(
            tenant=self.tenant,
            teacher=self.teacher,
            subject=self.subject,
            school_class=self.school_class,
            title="Quiz 1",
            total_marks=3,
        )
        self.q1 = Question.objects.create(
            tenant=self.tenant,
            assessment=self.assessment,
            text="A?",
            q_type="mcq",
            options=["x", "y"],
            correct_index=1,
            marks=1,
        )
        self.q2 = Question.objects.create(
            tenant=self.tenant,
            assessment=self.assessment,
            text="B?",
            q_type="mcq",
            options=["x", "y"],
            correct_index=0,
            marks=2,
        )

    def auth(self, user):
        token = self.client.post(
            reverse("core:token_obtain"),
            {"username": user.username, "password": "pass12345"},
            content_type="application/json",
        ).json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return self.client


class AutoGradeTests(BaseSchoolTest):
    def test_mcq_auto_grade(self):
        self.auth(self.student)
        resp = self.client.post(
            reverse("academics:submission-list"),
            {"assessment": self.assessment.id, "answers": {str(self.q1.id): 1, str(self.q2.id): 1}},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["is_graded"])
        self.assertEqual(resp.json()["score"], 1.0)  # q1 right (1) + q2 wrong (0)

    def test_resubmission_updates_not_duplicates(self):
        self.auth(self.student)
        payload = {"assessment": self.assessment.id, "answers": {str(self.q1.id): 1, str(self.q2.id): 0}}
        self.client.post(reverse("academics:submission-list"), payload, content_type="application/json")
        resp = self.client.post(
            reverse("academics:submission-list"),
            {**payload, "answers": {str(self.q1.id): 0, str(self.q2.id): 0}},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Submission.objects.filter(student=self.student).count(), 1)
        # q1 wrong (0) + q2 correct (2 marks) → 2.0, still one row (updated)
        self.assertEqual(resp.json()["score"], 2.0)

    def test_teacher_grade_marks_submission(self):
        submission = Submission.objects.create(
            tenant=self.tenant,
            assessment=self.assessment,
            student=self.student,
            answers={str(self.q1.id): 1},
        )
        self.auth(self.teacher)
        resp = self.client.post(
            reverse("academics:submission-grade", kwargs={"pk": submission.id}),
            {"score": 3, "feedback": "Good!"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        submission.refresh_from_db()
        self.assertTrue(submission.is_graded)
        self.assertEqual(submission.score, 3.0)
        self.assertTrue(submission.feedbacks.exists())


class ParentDashboardTests(BaseSchoolTest):
    def test_parent_sees_own_children(self):
        self.auth(self.parent)
        resp = self.client.get(reverse("academics:my-children"))
        self.assertEqual(resp.status_code, 200)
        names = [r["username"] for r in resp.json()["results"]]
        self.assertIn("student1", names)

    def test_parent_cannot_view_another_child(self):
        other = User.objects.create_user(
            username="stranger", password="pass12345",
            role=User.RoleChoice.STUDENT, tenant=self.tenant,
        )
        self.auth(self.parent)  # parent with no linked stranger
        Enrollment.objects.create(tenant=self.tenant, student=other, school_class=self.school_class)
        resp = self.client.get(
            reverse("academics:student-performance", kwargs={"student_id": other.id})
        )
        self.assertEqual(resp.status_code, 403)

    def test_performance_permits_own_child(self):
        self.auth(self.parent)
        resp = self.client.get(
            reverse("academics:student-performance", kwargs={"student_id": self.student.id})
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("subjects", resp.json())

    def test_summary_endpoint(self):
        # No LLM in tests → deterministic summary path.
        self.auth(self.parent)
        resp = self.client.get(
            reverse("academics:student-performance-summary", kwargs={"student_id": self.student.id})
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["summary"])


class NotificationAchievementTests(BaseSchoolTest):
    def test_admin_posts_notification_student_reads(self):
        self.auth(self.admin)
        resp = self.client.post(
            reverse("academics:notification-list"),
            {"title": "Holiday", "body": "No school", "audience": "students"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)

        self.auth(self.student)
        listed = self.client.get(reverse("academics:my-notifications"))
        self.assertEqual(listed.json()["count"], 1)
        mark = self.client.post(
            reverse("academics:notification-read", kwargs={"pk": resp.json()["id"]})
        )
        self.assertEqual(mark.status_code, 200)
        self.assertTrue(mark.json()["is_read"])

    def test_teacher_audience_excludes_student(self):
        self.auth(self.admin)
        self.client.post(
            reverse("academics:notification-list"),
            {"title": "Staff meeting", "body": "3pm", "audience": "teachers"},
            content_type="application/json",
        )
        self.auth(self.student)
        self.assertEqual(self.client.get(reverse("academics:my-notifications")).json()["count"], 0)

    def test_award_achievement_and_view(self):
        self.auth(self.admin)
        resp = self.client.post(
            reverse("academics:achievement-award"),
            {"title": "Star", "description": "Great", "awarded_to": self.student.id},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        self.auth(self.student)
        mine = self.client.get(reverse("academics:my-achievements"))
        self.assertEqual(mine.json()["count"], 1)


class StudentSelfStudyTests(BaseSchoolTest):
    def test_my_topics(self):
        self.auth(self.student)
        resp = self.client.get(reverse("academics:my-topics"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)

    def test_topic_questions_requires_generated_quiz(self):
        self.auth(self.student)
        resp = self.client.get(
            reverse("academics:topic-questions", kwargs={"topic_id": self.topic.id})
        )
        self.assertEqual(resp.status_code, 404)


class TenantIsolationTests(BaseSchoolTest):
    def test_teacher_only_sees_own_tenant_topics(self):
        other_tenant = Tenant.objects.create(name="Other", slug="other")
        other_class = SchoolClass.objects.create(tenant=other_tenant, name="6")
        other_subject = Subject.objects.create(tenant=other_tenant, name="History")
        other_teacher = User.objects.create_user(
            username="othert", password="pass12345",
            role=User.RoleChoice.TEACHER, tenant=other_tenant,
        )
        Topic.objects.create(
            tenant=other_tenant,
            teacher=other_teacher,
            subject=other_subject,
            school_class=other_class,
            title="Other Topic",
        )
        self.auth(self.teacher)
        resp = self.client.get(reverse("academics:topic-list"))
        titles = [r["title"] for r in resp.json()["results"]]
        self.assertNotIn("Other Topic", titles)
        self.assertIn("Photosynthesis", titles)
