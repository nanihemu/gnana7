from django.test import TestCase
from django.urls import reverse

from core.models import Tenant, User


class HealthAndAuthTests(TestCase):
    def test_health_endpoint(self):
        resp = self.client.get("/api/v1/health/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "ok")

    def test_token_obtain_and_me(self):
        user = User.objects.create_user(
            username="su", password="pass123",
            role=User.RoleChoice.SUPER_ADMIN,
        )
        resp = self.client.post(
            reverse("core:token_obtain"),
            {"username": "su", "password": "pass123"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        token = resp.json()["access"]
        me = self.client.get(
            reverse("core:me"), HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["username"], "su")


class TenantIsolationTests(TestCase):
    def setUp(self):
        self.sa = User.objects.create_user(
            username="su", password="pass123",
            role=User.RoleChoice.SUPER_ADMIN,
        )
        self.token = self.client.post(
            reverse("core:token_obtain"),
            {"username": "su", "password": "pass123"},
            content_type="application/json",
        ).json()["access"]

    def test_super_admin_creates_tenant(self):
        resp = self.client.post(
            reverse("tenants:tenant-list"),
            {"name": "Test School", "slug": "test-school"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Tenant.objects.count(), 1)