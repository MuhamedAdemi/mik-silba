from django.contrib.auth.models import User
from django.test import TestCase

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
