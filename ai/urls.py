from django.urls import path

from . import views

app_name = "ai"

urlpatterns = [
    path(
        "quiz/generate/<int:topic_id>/",
        views.GenerateQuizView.as_view(),
        name="quiz-generate",
    ),
    path(
        "quiz/jobs/<int:pk>/",
        views.QuizJobDetailView.as_view(),
        name="quiz-job-detail",
    ),
    path(
        "video/<int:topic_id>/",
        views.RequestVideoView.as_view(),
        name="video-request",
    ),
    path(
        "video/jobs/<int:pk>/",
        views.VideoJobDetailView.as_view(),
        name="video-job-detail",
    ),
]