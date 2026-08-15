from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import StaffProfile


class ReportsAccessTests(TestCase):
    def setUp(self):
        self.konobar = User.objects.create_user("konobar1", password="pass12345")
        self.admin = User.objects.create_user("shefi1", password="pass12345")
        self.admin.profile.role = StaffProfile.ADMIN
        self.admin.profile.save()

    def test_konobar_cannot_access_dashboard(self):
        self.client.login(username="konobar1", password="pass12345")
        response = self.client.get(reverse("reports:dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_dashboard(self):
        self.client.login(username="shefi1", password="pass12345")
        response = self.client.get(reverse("reports:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(reverse("reports:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)
