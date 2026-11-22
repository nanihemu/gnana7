from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import Tenant, User
from tenants.models import Plan, Subscription


class SuperAdminTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.superadmin = User.objects.create_user(
            username="su", password="pass12345",
            role=User.RoleChoice.SUPER_ADMIN,
        )
        token = self.client.post(
            reverse("core:token_obtain"),
            {"username": "su", "password": "pass12345"},
            content_type="application/json",
        ).json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_platform_stats(self):
        for i in range(3):
            Tenant.objects.create(name=f"S{i}", slug=f"s{i}")
        resp = self.client.get(reverse("tenants:platform-stats"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["tenants_total"], 3)
        self.assertIn("mrr_inr", resp.json())

    def test_plan_crud(self):
        resp = self.client.post(
            reverse("tenants:plan-list"),
            {"name": "Premium", "code": "premium", "monthly_price": "100.00"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        plan_id = resp.json()["id"]
        detail = self.client.get(reverse("tenants:plan-list"))
        self.assertEqual(detail.json()["count"], 1)

    def test_roles_list(self):
        resp = self.client.get(reverse("tenants:role-list"))
        self.assertEqual(resp.status_code, 200)

    def test_school_admin_cannot_access_platform(self):
        tenant = Tenant.objects.create(name="S", slug="s")
        school_admin = User.objects.create_user(
            username="admin", password="pass12345",
            role=User.RoleChoice.ADMIN, tenant=tenant,
        )
        token = self.client.post(
            reverse("core:token_obtain"),
            {"username": "admin", "password": "pass12345"},
            content_type="application/json",
        ).json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        resp = self.client.get(reverse("tenants:platform-stats"))
        self.assertEqual(resp.status_code, 403)

    def test_subscription_mrr(self):
        tenant = Tenant.objects.create(name="S", slug="s")
        plan = Plan.objects.create(name="Std", code="std", monthly_price="50.00")
        Subscription.objects.create(
            tenant=tenant, plan=plan,
            status=Subscription.Status.ACTIVE,
            starts_at="2026-01-01T00:00:00Z",
        )
        token = self.client.post(
            reverse("core:token_obtain"),
            {"username": "su", "password": "pass12345"},
            content_type="application/json",
        ).json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        resp = self.client.get(reverse("tenants:platform-stats"))
        self.assertEqual(resp.json()["active_subscriptions"], 1)
        self.assertEqual(float(resp.json()["mrr_inr"]), 50.0)
