from rest_framework import serializers

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


class SchoolClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolClass
        fields = ["id", "name", "section", "created_at"]


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "name", "code"]


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)

    class Meta:
        model = Enrollment
        fields = ["id", "student", "student_name", "school_class", "admission_number", "guardian"]
        read_only_fields = ["id"]


class TeacherSubjectAssignmentSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)

    class Meta:
        model = TeacherSubjectAssignment
        fields = ["id", "teacher", "teacher_name", "subject", "school_class"]


class TopicSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = Topic
        fields = [
            "id", "teacher", "teacher_name", "subject", "subject_name",
            "school_class", "title", "description", "material_file",
            "quiz_generated", "video_generated", "created_at",
        ]
        read_only_fields = ["id", "teacher", "created_at", "quiz_generated", "video_generated"]


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "text", "q_type", "options", "correct_index", "marks"]


class AssessmentSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = Assessment
        fields = [
            "id", "teacher", "teacher_name", "topic", "subject", "subject_name",
            "school_class", "title", "kind", "status", "total_marks",
            "duration_minutes", "is_ai_generated", "due_at", "created_at",
        ]
        read_only_fields = ["id", "teacher", "created_at"]


class SubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)

    class Meta:
        model = Submission
        fields = ["id", "assessment", "student", "student_name", "answers", "score", "is_graded", "submitted_at"]
        read_only_fields = ["id", "student", "score", "is_graded", "submitted_at"]


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["id", "submission", "teacher", "content", "is_ai_assisted", "created_at"]
        read_only_fields = ["id", "teacher", "created_at"]


class RemarkSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = Remark
        fields = ["id", "teacher", "teacher_name", "student", "subject", "subject_name", "content", "created_at"]
        read_only_fields = ["id", "teacher", "created_at"]