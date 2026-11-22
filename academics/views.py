from django.db.models import Count, Q
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.middleware import get_current_tenant
from core.permissions import (
    HasRole,
    IsParent,
    IsSchoolAdmin,
    IsStudent,
    IsTeacher,
)
from core.serializers import UserCreateSerializer, UserSerializer
from core.models import User

from .models import (
    Achievement,
    Assessment,
    Enrollment,
    Feedback,
    Notification,
    Question,
    Remark,
    SchoolClass,
    Subject,
    Submission,
    TeacherSubjectAssignment,
    Topic,
)
from .serializers import (
    AchievementSerializer,
    AssessmentSerializer,
    EnrollmentSerializer,
    FeedbackSerializer,
    NotificationSerializer,
    QuestionSerializer,
    RemarkSerializer,
    SchoolClassSerializer,
    SubjectSerializer,
    SubmissionSerializer,
    TeacherSubjectAssignmentSerializer,
    TopicSerializer,
)

# ---------------------------------------------------------------------------
# School Admin: structure
# ---------------------------------------------------------------------------


class ClassListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsSchoolAdmin]
    serializer_class = SchoolClassSerializer

    def get_queryset(self):
        return SchoolClass.objects.all()


class ClassDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSchoolAdmin]
    serializer_class = SchoolClassSerializer

    def get_queryset(self):
        return SchoolClass.objects.all()


class SubjectListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsSchoolAdmin]
    serializer_class = SubjectSerializer

    def get_queryset(self):
        return Subject.objects.all()


class SubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSchoolAdmin]
    serializer_class = SubjectSerializer

    def get_queryset(self):
        return Subject.objects.all()


class EnrollmentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsSchoolAdmin]
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        return Enrollment.objects.all().select_related("student", "school_class")


class EnrollmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSchoolAdmin]
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        return Enrollment.objects.all()


class TeacherAssignmentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsSchoolAdmin]
    serializer_class = TeacherSubjectAssignmentSerializer

    def get_queryset(self):
        return TeacherSubjectAssignment.objects.all().select_related(
            "teacher", "subject", "school_class"
        )


class TeacherAssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSchoolAdmin]
    serializer_class = TeacherSubjectAssignmentSerializer

    def get_queryset(self):
        return TeacherSubjectAssignment.objects.all()


# ---------------------------------------------------------------------------
# User provisioning (school admin creates students & teachers)
# ---------------------------------------------------------------------------


class ProvisionUserView(generics.CreateAPIView):
    """School Admin creates a student/teacher account within their tenant."""

    permission_classes = [IsSchoolAdmin]
    serializer_class = UserCreateSerializer

    def perform_create(self, serializer):
        serializer.save(tenant=get_current_tenant())


class ListUsersView(generics.ListAPIView):
    """School Admin lists users in their tenant, optionally filtered by role."""

    permission_classes = [IsSchoolAdmin]
    serializer_class = UserSerializer

    def get_queryset(self):
        # User is not a TenantModel, so scope explicitly to the school.
        qs = User.objects.filter(tenant=self.request.user.tenant)
        role = self.request.query_params.get("role")
        if role:
            qs = qs.filter(role=role)
        return qs.order_by("id")


# ---------------------------------------------------------------------------
# Teacher: topics, assessments, marks, feedback, remarks
# ---------------------------------------------------------------------------


class TopicListCreateView(generics.ListCreateAPIView):
    permission_classes = [HasRole(["admin", "teacher"])]
    serializer_class = TopicSerializer

    def get_queryset(self):
        return Topic.objects.all().select_related("teacher", "subject", "school_class")

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class TopicDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasRole(["admin", "teacher", "student", "parent"])]
    serializer_class = TopicSerializer

    def get_queryset(self):
        return Topic.objects.all().select_related("teacher", "subject", "school_class")


class AssessmentListCreateView(generics.ListCreateAPIView):
    permission_classes = [HasRole(["admin", "teacher"])]
    serializer_class = AssessmentSerializer

    def get_queryset(self):
        return Assessment.objects.all().select_related("teacher", "subject", "school_class")

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class AssessmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasRole(["admin", "teacher", "student"])]
    serializer_class = AssessmentSerializer

    def get_queryset(self):
        return Assessment.objects.all()


class QuestionListCreateView(generics.ListCreateAPIView):
    permission_classes = [HasRole(["admin", "teacher"])]
    serializer_class = QuestionSerializer

    def get_queryset(self):
        qs = Question.objects.all()
        assessment_id = self.request.query_params.get("assessment")
        if assessment_id:
            qs = qs.filter(assessment_id=assessment_id)
        topic_id = self.request.query_params.get("topic")
        if topic_id:
            qs = qs.filter(topic_id=topic_id)
        return qs.order_by("id")


class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasRole(["admin", "teacher"])]
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.all()


class SubmissionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsStudent]
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        return Submission.objects.filter(student=self.request.user).select_related("assessment")

    def create(self, request, *args, **kwargs):
        # One submission per assessment per student: re-submitting updates the
        # existing answer and re-grades it.
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assessment = serializer.validated_data["assessment"]
        submission, _ = Submission.objects.update_or_create(
            tenant=self.request.user.tenant,
            assessment=assessment,
            student=self.request.user,
            defaults={"answers": serializer.validated_data.get("answers", {})},
        )
        # Auto-grade MCQ answers immediately so students get instant feedback.
        from .services import auto_grade

        auto_grade(submission)
        return Response(
            SubmissionSerializer(submission).data, status=status.HTTP_200_OK
        )


class SubmissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasRole(["teacher", "student"])]
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        return Submission.objects.all()


class TeacherSubmissionListView(generics.ListAPIView):
    """Teacher/Admin: submissions across the school, for grading queue."""

    permission_classes = [HasRole(["admin", "teacher"])]
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        qs = Submission.objects.all().select_related("assessment", "student")
        graded = self.request.query_params.get("graded")
        if graded is not None:
            qs = qs.filter(is_graded=graded.lower() in ("1", "true", "yes"))
        return qs.order_by("-submitted_at")


class GradeSubmissionView(APIView):
    """Teacher grades a written/assignment submission and marks it graded."""

    permission_classes = [HasRole(["admin", "teacher"])]

    def post(self, request, pk):
        from .services import teacher_grade

        try:
            submission = Submission.objects.get(pk=pk)
        except Submission.DoesNotExist:
            return Response({"detail": "Submission not found."}, status=status.HTTP_404_NOT_FOUND)

        score = request.data.get("score")
        if score is None:
            return Response(
                {"detail": "score is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            score = float(score)
        except (TypeError, ValueError):
            return Response(
                {"detail": "score must be a number."}, status=status.HTTP_400_BAD_REQUEST
            )

        teacher_grade(submission, score)

        feedback_text = request.data.get("feedback")
        if feedback_text:
            from .models import Feedback

            Feedback.objects.create(
                tenant=submission.tenant,
                submission=submission,
                teacher=request.user,
                content=feedback_text,
            )

        return Response(SubmissionSerializer(submission).data)


class FeedbackListCreateView(generics.ListCreateAPIView):
    permission_classes = [HasRole(["admin", "teacher"])]
    serializer_class = FeedbackSerializer

    def get_queryset(self):
        return Feedback.objects.all()

    def perform_create(self, serializer):
        serializer.save(tenant=get_current_tenant(), teacher=self.request.user)


class RemarkListCreateView(generics.ListCreateAPIView):
    permission_classes = [HasRole(["admin", "teacher"])]
    serializer_class = RemarkSerializer

    def get_queryset(self):
        return Remark.objects.all().select_related("teacher", "subject")

    def perform_create(self, serializer):
        serializer.save(tenant=get_current_tenant(), teacher=self.request.user)


# ---------------------------------------------------------------------------
# Students: their assessments & results
# ---------------------------------------------------------------------------


class MyAssessmentsView(generics.ListAPIView):
    """Assessments published for the student's class (for practice/attempt)."""

    permission_classes = [IsStudent]
    serializer_class = AssessmentSerializer

    def get_queryset(self):
        enrollment = Enrollment.objects.filter(student=self.request.user).first()
        if not enrollment:
            return Assessment.objects.none()
        return Assessment.objects.filter(
            school_class=enrollment.school_class,
            status=Assessment.Status.PUBLISHED,
        ).select_related("subject")


class MyResultsView(generics.ListAPIView):
    """The student's own graded submissions."""

    permission_classes = [IsStudent]
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        return Submission.objects.filter(
            student=self.request.user, is_graded=True
        ).select_related("assessment")


class AssessmentQuestionsView(APIView):
    """Student: questions for a published assessment in their class (answers hidden)."""

    permission_classes = [IsStudent]

    def get(self, request, assessment_id):
        from .models import Assessment

        try:
            assessment = Assessment.objects.get(pk=assessment_id)
        except Assessment.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        enrollment = Enrollment.objects.filter(student=request.user).first()
        available = (
            enrollment
            and assessment.school_class_id == enrollment.school_class_id
            and assessment.status == Assessment.Status.PUBLISHED
        )
        if not available:
            return Response(
                {"detail": "This assessment is not available to you."},
                status=status.HTTP_403_FORBIDDEN,
            )

        qs = Question.objects.filter(assessment=assessment).order_by("id")
        data = [
            {
                "id": q.id,
                "text": q.text,
                "q_type": q.q_type,
                "options": q.options,
                "marks": q.marks,
            }
            for q in qs
        ]
        return Response(
            {
                "assessment": assessment.id,
                "title": assessment.title,
                "total_marks": assessment.total_marks,
                "questions": data,
            }
        )


# ---------------------------------------------------------------------------
# Student performance analytics (also consumed by parents)
# ---------------------------------------------------------------------------


def compute_performance(student_id):
    """
    Subject-wise performance for a student: percentage per subject and flagged
    strong/weak areas. Score is the fraction of the assessment's total marks
    that the student earned, expressed as a percentage (0-100).
    """
    submissions = (
        Submission.objects.filter(student_id=student_id, is_graded=True)
        .select_related("assessment", "assessment__subject")
        .prefetch_related("assessment__questions")
    )
    by_subject = {}
    for sub in submissions:
        subject = sub.assessment.subject.name
        # Prefer the assessment's declared total; fall back to summing its
        # questions so percentages don't silently become 0%.
        total_marks = sub.assessment.total_marks or sum(
            q.marks for q in sub.assessment.questions.all()
        )
        entry = by_subject.setdefault(subject, {"earned": 0.0, "possible": 0.0, "count": 0})
        entry["earned"] += sub.score or 0
        entry["possible"] += total_marks
        entry["count"] += 1

    subjects = []
    for name, e in by_subject.items():
        pct = round((e["earned"] / e["possible"]) * 100, 2) if e["possible"] else 0.0
        status_label = "strong" if pct >= 75 else ("average" if pct >= 50 else "weak")
        subjects.append({"subject": name, "percentage": pct, "status": status_label})

    return {"student_id": student_id, "subjects": subjects}


class StudentPerformanceView(APIView):
    """
    Subject-wise performance for a student: percentage per subject and flagged
    strong/weak areas. Parents use this for their child; students use it for
    their own dashboard.
    """

    permission_classes = [HasRole(["student", "parent", "admin"])]

    def get(self, request, student_id):
        if request.user.role == request.user.RoleChoice.PARENT:
            # Parents can only see their own children.
            parented = Enrollment.objects.filter(
                guardian=request.user, student_id=student_id
            ).exists()
            if not parented:
                return Response(
                    {"detail": "This is not one of your children."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        elif request.user.role == request.user.RoleChoice.STUDENT:
            # Students can only see their own performance.
            if request.user.id != student_id:
                return Response(
                    {"detail": "You can only view your own performance."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        return Response(compute_performance(student_id))


class ParentSummaryView(APIView):
    """
    AI-generated natural-language summary of a child's performance for parents,
    describing weak/strong areas and suggesting a next step. Falls back to a
    deterministic summary when no LLM is configured.
    """

    permission_classes = [HasRole(["parent", "student", "admin"])]

    def get(self, request, student_id):
        if request.user.role == request.user.RoleChoice.PARENT:
            parented = Enrollment.objects.filter(
                guardian=request.user, student_id=student_id
            ).exists()
            if not parented:
                return Response(
                    {"detail": "This is not one of your children."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        elif request.user.role == request.user.RoleChoice.STUDENT and request.user.id != student_id:
            return Response(
                {"detail": "You can only view your own summary."},
                status=status.HTTP_403_FORBIDDEN,
            )

        performance = compute_performance(student_id)
        student = User.objects.filter(pk=student_id).first()
        child_name = student.full_name or student.username if student else "your child"
        from ai.services.summary import parent_progress_summary

        summary = parent_progress_summary(child_name, performance["subjects"])
        return Response({"student_id": student_id, "summary": summary})


class MyChildrenView(generics.ListAPIView):
    """Parent dashboard: list the parent's children (enrolled students)."""

    permission_classes = [IsParent]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(
            id__in=Enrollment.objects.filter(guardian=self.request.user).values("student_id")
        ).order_by("id")


# ---------------------------------------------------------------------------
# Notifications (admin posts, everyone reads)
# ---------------------------------------------------------------------------


class NotificationListCreateView(generics.ListCreateAPIView):
    """School admin posts notifications; every user lists those aimed at their role."""

    permission_classes = [HasRole(["admin"])]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        qs = Notification.objects.all()
        audience = self.request.query_params.get("audience")
        if audience:
            qs = qs.filter(audience=audience)
        return qs

    def perform_create(self, serializer):
        serializer.save(tenant=get_current_tenant(), created_by=self.request.user)


class MyNotificationsView(generics.ListAPIView):
    """A user's notifications, filtered to their role's audience."""

    permission_classes = [HasRole(["admin", "teacher", "student", "parent"])]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        role = self.request.user.role
        if role in (User.RoleChoice.ADMIN,):
            audiences = [Notification.Audience.ALL, Notification.Audience.ADMIN]
        elif role == User.RoleChoice.TEACHER:
            audiences = [Notification.Audience.ALL, Notification.Audience.TEACHERS]
        elif role == User.RoleChoice.STUDENT:
            audiences = [Notification.Audience.ALL, Notification.Audience.STUDENTS]
        else:  # parent
            audiences = [Notification.Audience.ALL, Notification.Audience.PARENTS]
        return Notification.objects.filter(audience__in=audiences)


class MarkNotificationReadView(APIView):
    """Mark one (or all) notifications as read for the current user."""

    permission_classes = [HasRole(["admin", "teacher", "student", "parent"])]

    def post(self, request, pk=None):
        if pk:
            try:
                note = Notification.objects.get(pk=pk)
            except Notification.DoesNotExist:
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
            note.read_by.add(request.user)
            return Response(NotificationSerializer(note, context={"request": request}).data)
        # mark all as read — same audience filter as MyNotificationsView
        role = request.user.role
        if role in (User.RoleChoice.ADMIN,):
            audiences = [Notification.Audience.ALL, Notification.Audience.ADMIN]
        elif role == User.RoleChoice.TEACHER:
            audiences = [Notification.Audience.ALL, Notification.Audience.TEACHERS]
        elif role == User.RoleChoice.STUDENT:
            audiences = [Notification.Audience.ALL, Notification.Audience.STUDENTS]
        else:  # parent
            audiences = [Notification.Audience.ALL, Notification.Audience.PARENTS]
        notes = Notification.objects.filter(audience__in=audiences)
        for note in notes:
            note.read_by.add(request.user)
        return Response({"marked": notes.count()})


# ---------------------------------------------------------------------------
# Achievements (school awards to students)
# ---------------------------------------------------------------------------


class AchievementCreateView(generics.CreateAPIView):
    """Admin/teacher awards an achievement to a student."""

    permission_classes = [HasRole(["admin", "teacher"])]
    serializer_class = AchievementSerializer

    def perform_create(self, serializer):
        serializer.save(tenant=get_current_tenant(), awarded_by=self.request.user)


class AchievementListCreateView(generics.ListCreateAPIView):
    permission_classes = [HasRole(["admin", "teacher"])]
    serializer_class = AchievementSerializer

    def get_queryset(self):
        return Achievement.objects.all().select_related("awarded_to")


class StudentAchievementsView(generics.ListAPIView):
    """List achievements for one student (students self-view, parents their child)."""

    permission_classes = [HasRole(["student", "parent", "admin", "teacher"])]
    serializer_class = AchievementSerializer

    def get_queryset(self):
        return Achievement.objects.filter(awarded_to_id=self.kwargs["student_id"])


class MyAchievementsView(generics.ListAPIView):
    """The student's own achievements."""

    permission_classes = [IsStudent]
    serializer_class = AchievementSerializer

    def get_queryset(self):
        return Achievement.objects.filter(awarded_to=self.request.user)


# ---------------------------------------------------------------------------
# Students: self-study topics (with AI quizzes & videos)
# ---------------------------------------------------------------------------


class MyTopicsView(generics.ListAPIView):
    """Topics posted for the student's class — self-study material with AI quiz/video flags."""

    permission_classes = [IsStudent]
    serializer_class = TopicSerializer

    def get_queryset(self):
        enrollment = Enrollment.objects.filter(student=self.request.user).first()
        if not enrollment:
            return Topic.objects.none()
        return Topic.objects.filter(school_class=enrollment.school_class).select_related(
            "teacher", "subject"
        )


class TopicQuestionsView(APIView):
    """The questions for a topic's AI quiz (students practice self-study)."""

    permission_classes = [HasRole(["student", "parent", "teacher", "admin"])]

    def get(self, request, topic_id):
        from .models import Question

        questions = Question.objects.filter(topic_id=topic_id).order_by("id")
        if not questions:
            return Response({"detail": "No quiz generated for this topic yet."}, status=404)
        # Hide correct answers from students until they've submitted.
        data = []
        for q in questions:
            data.append(
                {
                    "id": q.id,
                    "text": q.text,
                    "q_type": q.q_type,
                    "options": q.options,
                    "marks": q.marks,
                }
            )
        return Response({"topic_id": topic_id, "questions": data})