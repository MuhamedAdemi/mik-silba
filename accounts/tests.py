from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import StaffProfile


class StaffProfileSignalTests(TestCase):
    def test_regular_user_gets_konobar_profile(self):
        user = User.objects.create_user("kelner", password="x")
        self.assertEqual(user.profile.role, StaffProfile.KONOBAR)
        self.assertFalse(user.profile.is_admin)

    def test_superuser_gets_admin_profile(self):
        user = User.objects.create_superuser("shefi", "shefi@example.com", "x")
        self.assertEqual(user.profile.role, StaffProfile.ADMIN)
        self.assertTrue(user.profile.is_admin)


class LanguageSwitchTests(TestCase):
    def test_default_language_is_croatian(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertContains(response, "Prijava")

    def test_switch_to_english(self):
        self.client.post(reverse("accounts:set_language", args=["en"]), {"next": reverse("accounts:login")})
        response = self.client.get(reverse("accounts:login"))
        self.assertContains(response, "Log in")

    def test_switch_to_albanian(self):
        self.client.post(reverse("accounts:set_language", args=["sq"]), {"next": reverse("accounts:login")})
        response = self.client.get(reverse("accounts:login"))
        self.assertContains(response, "Kyçu")

    def test_invalid_language_code_is_ignored(self):
        self.client.post(reverse("accounts:set_language", args=["de"]), {"next": reverse("accounts:login")})
        response = self.client.get(reverse("accounts:login"))
        self.assertContains(response, "Prijava")
