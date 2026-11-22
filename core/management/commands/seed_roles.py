"""Seed initial roles and a platform super admin so the API is usable immediately."""

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Role, User

DEFAULT_ROLES = {
    "super_admin": {
        "name": "Super Admin",
        "permissions": [
            "tenant.manage", "tenant.create", "tenant.suspend",
            "plan.manage", "subscription.manage", "role.manage",
            "platform.stats", "transaction.view",
        ],
    },
    "admin": {
        "name": "School Admin",
        "permissions": [
            "student.write", "teacher.write", "class.write", "subject.write",
            "enrollment.write", "assessment.write", "notification.write",
            "school.stats", "payment.view", "achievement.write",
        ],
    },
    "teacher": {
        "name": "Teacher",
        "permissions": [
            "topic.write", "assessment.write", "mark.write",
            "feedback.write", "remark.write", "quiz.generate", "video.generate",
        ],
    },
    "student": {
        "name": "Student",
        "permissions": [
            "assessment.attempt", "performance.view", "topic.view",
            "communication.read", "quiz.attempt",
        ],
    },
    "parent": {
        "name": "Parent",
        "permissions": [
            "child.performance.view", "child.suggestion.view", "payment.view",
        ],
    },
}


class Command(BaseCommand):
    help = "Seed default roles and a platform super admin."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username", default="superadmin", help="Super admin username"
        )
        parser.add_argument(
            "--password", default="changeme123", help="Super admin password"
        )
        parser.add_argument(
            "--email", default="admin@sms.local", help="Super admin email"
        )

    @transaction.atomic
    def handle(self, *args, **options):
        created_roles = []
        for code, data in DEFAULT_ROLES.items():
            _, created = Role.objects.get_or_create(
                code=code,
                defaults={"name": data["name"], "permissions": data["permissions"]},
            )
            created_roles.append((code, created))

        for code, created in created_roles:
            self.stdout.write(
                self.style.SUCCESS(f"role {code}: {'created' if created else 'exists'}")
            )

        username = options["username"]
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=options["email"],
                password=options["password"],
                role=User.RoleChoice.SUPER_ADMIN,
                full_name="Platform Super Admin",
            )
            self.stdout.write(
                self.style.SUCCESS(f"super admin created: {username}")
            )
        else:
            self.stdout.write(f"super admin '{username}' already exists")