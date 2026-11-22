from django.urls import path

from . import views

app_name = "academics"

urlpatterns = [
    # School admin: structure
    path("classes/", views.ClassListCreateView.as_view(), name="class-list"),
    path("classes/<int:pk>/", views.ClassDetailView.as_view(), name="class-detail"),
    path("subjects/", views.SubjectListCreateView.as_view(), name="subject-list"),
    path("subjects/<int:pk>/", views.SubjectDetailView.as_view(), name="subject-detail"),
    path("enrollments/", views.EnrollmentListCreateView.as_view(), name="enrollment-list"),
    path("enrollments/<int:pk>/", views.EnrollmentDetailView.as_view(), name="enrollment-detail"),
    path(
        "teacher-assignments/",
        views.TeacherAssignmentListCreateView.as_view(),
        name="teacher-assignment-list",
    ),
    path(
        "teacher-assignments/<int:pk>/",
        views.TeacherAssignmentDetailView.as_view(),
        name="teacher-assignment-detail",
    ),
    # User provisioning
    path("users/", views.ListUsersView.as_view(), name="user-list"),
    path("users/provision/", views.ProvisionUserView.as_view(), name="user-provision"),
    # Teacher content
    path("topics/", views.TopicListCreateView.as_view(), name="topic-list"),
    path("topics/<int:pk>/", views.TopicDetailView.as_view(), name="topic-detail"),
    path("assessments/", views.AssessmentListCreateView.as_view(), name="assessment-list"),
    path("assessments/<int:pk>/", views.AssessmentDetailView.as_view(), name="assessment-detail"),
    path("questions/", views.QuestionListCreateView.as_view(), name="question-list"),
    path("questions/<int:pk>/", views.QuestionDetailView.as_view(), name="question-detail"),
    path("submissions/", views.SubmissionListCreateView.as_view(), name="submission-list"),
    path("submissions/<int:pk>/", views.SubmissionDetailView.as_view(), name="submission-detail"),
    path("feedback/", views.FeedbackListCreateView.as_view(), name="feedback-list"),
    path("remarks/", views.RemarkListCreateView.as_view(), name="remark-list"),
    # Student views
    path("me/assessments/", views.MyAssessmentsView.as_view(), name="my-assessments"),
    path("me/results/", views.MyResultsView.as_view(), name="my-results"),
    # Analytics
    path("performance/<int:student_id>/", views.StudentPerformanceView.as_view(), name="student-performance"),
]