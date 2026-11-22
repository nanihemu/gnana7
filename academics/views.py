from django.db.models import Count, Q
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.middleware import get_current_tenant
from core.permissions import HasRole, IsSchoolAdmin, IsStudent, IsTeacher
from core.serializers import UserCreateSerializer, UserSerializer
from core.models import User

from .models import (
    Assessment,
    Enrollment,
    Feedback,
    Question,
    Remark,
    SchoolClass,
    Subject,
    Submission,
    TeacherSubjectAssignment,
    Topic,
)
from .serializers import (
    AssessmentSerializer,
    EnrollmentSerializer,
    FeedbackSerializer,
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
    queryset = SchoolClass.objects.all()


class ClassDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSchoolAdmin]
    serializer_class = SchoolClassSerializer
    queryset = SchoolClass.objects.all()


class SubjectListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsSchoolAdmin]
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all()


class SubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSchoolAdmin]
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all()


class EnrollmentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsSchoolAdmin]
    serializer_class = EnrollmentSerializer
    queryset = Enrollment.objects.all().select_related("student", "school_class")


class EnrollmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSchoolAdmin]
    serializer_class = EnrollmentSerializer
    queryset = Enrollment.objects.all()


class TeacherAssignmentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsSchoolAdmin]
    serializer_class = TeacherSubjectAssignmentSerializer
    queryset = TeacherSubjectAssignment.objects.all().select_related("teacher", "subject", "school_class")


class TeacherAssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSchoolAdmin]
    serializer_class = TeacherSubjectAssignmentSerializer
    queryset = TeacherSubjectAssignment.objects.all()


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
        qs = User.objects.all()
        role = self.request.query_params.get("role")
        if role:
            qs = qs.filter(role=role)
        return qs


# ---------------------------------------------------------------------------
# Teacher: topics, assessments, marks, feedback, remarks
# ---------------------------------------------------------------------------


class TopicListCreateView(generics.ListCreateAPIView):
    permission_classes = [HasRole(["admin", "teacher"])]
    serializer_class = TopicSerializer
    queryset = Topic.objects.all().select_related("teacher", "subject", "school_class")

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class TopicDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasRole(["admin", "teacher", "student", "parent"])]
    serializer_class = TopicSerializer
    queryset = Topic.objects.all().select_related("teacher", "subject", "school_class")


class AssessmentListCreateView(generics.ListCreateAPIView):
    permission_classes = [HasRole(["admin", "teacher"])]
    serializer_class = AssessmentSerializer
    queryset = Assessment.objects.all().select_related("teacher", "subject", "school_class")

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class AssessmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasRole(["admin", "teacher", "student"])]
    serializer_class = AssessmentSerializer
    queryset = Assessment.objects.all()


class QuestionListCreateView(generics.ListCreateAPIView):
    permission_classes = [HasRole(["admin", "teacher"])]
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()


class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasRole(["admin", "teacher"])]
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()


class SubmissionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsStudent]
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        return Submission.objects.filter(student=self.request.user).select_related("assessment")

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class SubmissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasRole(["teacher", "student"])]
    serializer_class = SubmissionSerializer
    queryset = Submission.objects.all()


class FeedbackListCreateView(generics.ListCreateAPIView):
    permission_classes = [HasRole(["admin", "teacher"])]
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class RemarkListCreateView(generics.ListCreateAPIView):
    permission_classes = [HasRole(["admin", "teacher"])]
    serializer_class = RemarkSerializer
    queryset = Remark.objects.all().select_related("teacher", "subject")

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


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


# ---------------------------------------------------------------------------
# Student performance analytics (also consumed by parents)
# ---------------------------------------------------------------------------


class StudentPerformanceView(APIView):
    """
    Subject-wise performance for a student: average score per subject and
    flagged strong/weak areas. Parents use this for their child; students use
    it for their own dashboard.
    """

    permission_classes = [HasRole(["student", "parent", "admin"])]

    def get(self, request, student_id):
        submissions = Submission.objects.filter(student_id=student_id, is_graded=True).select_related("assessment__subject")
        by_subject = {}
        for sub in submissions:
            subject = sub.assessment.subject.name
            entry = by_subject.setdefault(subject, {"total": 0.0, "count": 0})
            entry["total"] += sub.score
            entry["count"] += 1

        subjects = []
        for name, e in by_subject.items():
            avg = round(e["total"] / e["count"], 2)
            status_label = "strong" if avg >= 75 else ("average" if avg >= 50 else "weak")
            subjects.append({"subject": name, "average": avg, "status": status_label})

        return Response({"student_id": student_id, "subjects": subjects})