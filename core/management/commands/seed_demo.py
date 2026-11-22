"""Seed a demo school with users, content, and AI-flavored data for local dev."""

from django.core.management.base import BaseCommand
from django.db import transaction

from academics.models import (
    Achievement,
    Assessment,
    Enrollment,
    Notification,
    Question,
    SchoolClass,
    Subject,
    TeacherSubjectAssignment,
    Topic,
)
from core.models import Tenant, User

DEMO_PASSWORD = "demo12345"


class Command(BaseCommand):
    help = "Create a demo tenant + one user per role with known credentials."

    def add_arguments(self, parser):
        parser.add_argument(
            "--slug", default="demo", help="Tenant slug (default: demo)"
        )

    @transaction.atomic
    def handle(self, *args, **options):
        slug = options["slug"]
        tenant, created = Tenant.objects.get_or_create(
            slug=slug, defaults={"name": "Demo School", "contact_email": "demo@sms.local"}
        )
        if not created and not User.objects.filter(tenant=tenant).exists():
            pass  # re-seeding a tenant that already has users → skip content
        self.stdout.write(f"tenant '{slug}': {'created' if created else 'exists'}")

        def make_user(username, role, full_name):
            user, u_created = User.objects.get_or_create(
                username=username,
                defaults={
                    "tenant": tenant,
                    "role": role,
                    "full_name": full_name,
                    "is_verified": True,
                },
            )
            user.set_password(DEMO_PASSWORD)
            user.save()
            if u_created:
                self.stdout.write(f"  user {username} ({role}) created")
            return user

        admin = make_user("admin", User.RoleChoice.ADMIN, "School Admin")
        teacher = make_user("teacher", User.RoleChoice.TEACHER, "Ms. Teacher")
        student1 = make_user("student", User.RoleChoice.STUDENT, "Arjun Kumar")
        student2 = make_user("student2", User.RoleChoice.STUDENT, "Priya Sharma")
        parent = make_user("parent", User.RoleChoice.PARENT, "Ravi Kumar")

        # Super admin exists globally from seed_roles; ensure a password for it too.
        superadmin, _ = User.objects.get_or_create(
            username="superadmin", defaults={"role": User.RoleChoice.SUPER_ADMIN}
        )
        superadmin.set_password("changeme123")
        superadmin.save()

        if not SchoolClass.objects.filter(tenant=tenant).exists():
            cls6 = SchoolClass.objects.create(tenant=tenant, name="6", section="A")
            cls7 = SchoolClass.objects.create(tenant=tenant, name="7", section="A")
            science = Subject.objects.create(tenant=tenant, name="Science", code="SCI")
            maths = Subject.objects.create(tenant=tenant, name="Mathematics", code="MATH")

            TeacherSubjectAssignment.objects.create(
                tenant=tenant, teacher=teacher, subject=science, school_class=cls6
            )
            TeacherSubjectAssignment.objects.create(
                tenant=tenant, teacher=teacher, subject=maths, school_class=cls6
            )

            Enrollment.objects.create(
                tenant=tenant, student=student1, school_class=cls6, guardian=parent
            )
            Enrollment.objects.create(
                tenant=tenant, student=student2, school_class=cls7
            )

            t1 = Topic.objects.create(
                tenant=tenant,
                teacher=teacher,
                subject=science,
                school_class=cls6,
                title="Photosynthesis",
                description="Plants make food using sunlight, water and carbon dioxide in chloroplasts, releasing oxygen.",
            )
            t2 = Topic.objects.create(
                tenant=tenant,
                teacher=teacher,
                subject=maths,
                school_class=cls6,
                title="Fractions",
                description="Understanding parts of a whole; numerator and denominator.",
            )

            quiz = Assessment.objects.create(
                tenant=tenant,
                teacher=teacher,
                subject=science,
                school_class=cls6,
                title="Photosynthesis Quiz",
                kind=Assessment.Kind.QUIZ,
                status=Assessment.Status.PUBLISHED,
                total_marks=5,
            )
            qs = [
                ("Where do plants make food?", ["Roots", "Chloroplast", "Stem", "Flower"], 1, 1),
                ("Which gas do plants release?", ["CO2", "O2", "N2", "H2"], 1, 2),
                ("Plants need sunlight to ______.", ["photosynthesize", "sleep", "decay", "freeze"], 0, 2),
            ]
            for text, options, correct, marks in qs:
                Question.objects.create(
                    tenant=tenant,
                    assessment=quiz,
                    q_type="mcq",
                    text=text,
                    options=options,
                    correct_index=correct,
                    marks=marks,
                )

            Notification.objects.create(
                tenant=tenant,
                created_by=admin,
                title="Welcome to the new term",
                body="All classes resume tomorrow at 8:00 AM.",
                audience=Notification.Audience.ALL,
            )
            Notification.objects.create(
                tenant=tenant,
                created_by=admin,
                title="Sports Day",
                body="Annual sports day will be held on Dec 5.",
                audience=Notification.Audience.STUDENTS,
            )
            Achievement.objects.create(
                tenant=tenant,
                awarded_by=admin,
                awarded_to=student1,
                title="Star Student",
                description="Great performance in Science this month.",
                icon="star",
            )
            self.stdout.write("  demo class/subject/topic/quiz/notification data created")

            # Index topics for the chatbot.
            from ai.services.rag import index_topic

            for t in (t1, t2):
                try:
                    index_topic(t)
                except Exception:  # noqa: BLE001 - offline, embedding may be unavailable
                    pass

        self.stdout.write(
            self.style.SUCCESS(
                "Demo ready. Logins (password demo12345): superadmin/changeme123, "
                "admin, teacher, student, student2, parent"
            )
        )
