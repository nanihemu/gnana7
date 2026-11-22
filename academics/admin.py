from django.contrib import admin

from .models import Achievement, Assessment, Enrollment, Feedback, Notification, Question, Remark, SchoolClass, Subject, Submission, TeacherSubjectAssignment, Topic


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ("name", "section", "tenant")
    search_fields = ("name",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "tenant")
    search_fields = ("name",)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "teacher", "quiz_generated", "video_generated")
    list_filter = ("quiz_generated", "video_generated")
    search_fields = ("title",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "school_class", "guardian")


@admin.register(TeacherSubjectAssignment)
class TeacherSubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ("teacher", "subject", "school_class")


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "status", "subject", "school_class", "total_marks")
    list_filter = ("kind", "status")
    search_fields = ("title",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "q_type", "marks")
    list_filter = ("q_type",)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("student", "assessment", "score", "is_graded", "submitted_at")
    list_filter = ("is_graded",)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("submission", "teacher", "is_ai_assisted")


@admin.register(Remark)
class RemarkAdmin(admin.ModelAdmin):
    list_display = ("teacher", "student", "subject", "created_at")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "audience", "created_by", "created_at")
    list_filter = ("audience",)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("title", "awarded_to", "awarded_by", "created_at")
