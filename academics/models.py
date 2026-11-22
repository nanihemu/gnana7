from django.db import models

from core.managers import TenantModel


class SchoolClass(TenantModel):
    """A grade/class, e.g. 'Class 6'. Tenant-scoped via TenantModel."""

    name = models.CharField(max_length=50)
    section = models.CharField(max_length=10, blank=True, default="A")

    class Meta:
        db_table = "school_classes"
        ordering = ["name", "section"]
        unique_together = [("tenant", "name", "section")]

    def __str__(self):
        return f"{self.name} - {self.section}"


class Subject(TenantModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = "subjects"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Topic(TenantModel):
    """
    A lesson topic posted by a teacher, with an optional description/material.
    This is the input for the AI quiz generator and the AI video pipeline.
    """

    teacher = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="topics"
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="topics")
    school_class = models.ForeignKey(
        SchoolClass, on_delete=models.CASCADE, related_name="topics"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    material_file = models.FileField(upload_to="topics/", null=True, blank=True)
    quiz_generated = models.BooleanField(default=False)
    video_generated = models.BooleanField(default=False)

    class Meta:
        db_table = "topics"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Enrollment(TenantModel):
    """A student enrolled in a class. student is a user with role=student."""

    student = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="enrollments"
    )
    school_class = models.ForeignKey(
        SchoolClass, on_delete=models.CASCADE, related_name="enrollments"
    )
    admission_number = models.CharField(max_length=30, blank=True)
    guardian = models.ForeignKey(
        "core.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="wards", help_text="Linked parent account",
    )

    class Meta:
        db_table = "enrollments"
        unique_together = [("tenant", "student", "school_class")]

    def __str__(self):
        return f"{self.student} in {self.school_class}"


class TeacherSubjectAssignment(TenantModel):
    """Which teacher teaches which subject to which class."""

    teacher = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="teachings"
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="assignments")
    school_class = models.ForeignKey(
        SchoolClass, on_delete=models.CASCADE, related_name="assignments"
    )

    class Meta:
        db_table = "teacher_subject_assignments"
        unique_together = [("tenant", "teacher", "subject", "school_class")]

    def __str__(self):
        return f"{self.teacher} → {self.subject} ({self.school_class})"


class Assessment(TenantModel):
    """A quiz, assignment, or exam posted by a teacher for a class."""

    class Kind(models.TextChoices):
        QUIZ = "quiz", "Quiz"
        ASSIGNMENT = "assignment", "Assignment"
        EXAM = "exam", "Exam"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        CLOSED = "closed", "Closed"

    teacher = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="assessments"
    )
    topic = models.ForeignKey(
        Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name="assessments"
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="assessments")
    school_class = models.ForeignKey(
        SchoolClass, on_delete=models.CASCADE, related_name="assessments"
    )
    title = models.CharField(max_length=255)
    kind = models.CharField(max_length=15, choices=Kind.choices, default=Kind.QUIZ)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PUBLISHED)
    total_marks = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=10)
    is_ai_generated = models.BooleanField(default=False)
    due_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "assessments"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Question(TenantModel):
    """A question bank item. AI-generated quizzes populate these."""

    class QType(models.TextChoices):
        MCQ = "mcq", "Multiple Choice"
        SHORT = "short", "Short Answer"

    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="questions",
        null=True, blank=True,
    )
    topic = models.ForeignKey(
        Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name="questions"
    )
    text = models.TextField()
    q_type = models.CharField(max_length=10, choices=QType.choices, default=QType.MCQ)
    options = models.JSONField(default=list, help_text="For MCQ: list of option strings")
    correct_index = models.PositiveIntegerField(null=True, blank=True, help_text="For MCQ")
    marks = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "questions"

    def __str__(self):
        return self.text[:60]


class Submission(TenantModel):
    """A student's attempt at an assessment."""

    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="submissions"
    )
    student = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="submissions"
    )
    answers = models.JSONField(default=dict, help_text="question_id → answer")
    score = models.FloatField(null=True, blank=True)
    is_graded = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "submissions"
        unique_together = [("tenant", "assessment", "student")]

    def __str__(self):
        return f"{self.student} → {self.assessment}"


class Feedback(TenantModel):
    """Written and AI-assisted feedback a teacher gives on a submission."""

    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name="feedbacks"
    )
    teacher = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="feedbacks")
    content = models.TextField()
    is_ai_assisted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "feedbacks"

    def __str__(self):
        return f"Feedback on #{self.submission_id}"


class Remark(TenantModel):
    """Short remarks a teacher records about a student for their subject."""

    teacher = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="remarks")
    student = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="remarks_received")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="remarks")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "remarks"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.teacher} → {self.student}"
