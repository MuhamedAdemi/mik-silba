from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from orders.models import Order
from venue.models import Table, Zone

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


class StaffManagementTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser("muhamed", "m@example.com", "x")
        self.admin = User.objects.create_user("blerim", password="x")
        self.admin.profile.role = StaffProfile.ADMIN
        self.admin.profile.save()
        self.konobar = User.objects.create_user("konobar1", password="x")

    def test_konobar_cannot_access_staff_list(self):
        self.client.login(username="konobar1", password="x")
        response = self.client.get(reverse("accounts:staff_list"))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_staff_list(self):
        self.client.login(username="blerim", password="x")
        response = self.client.get(reverse("accounts:staff_list"))
        self.assertEqual(response.status_code, 200)

    def test_regular_admin_creating_staff_gets_konobar_role(self):
        self.client.login(username="blerim", password="x")
        self.client.post(reverse("accounts:staff_create"), {
            "username": "novikonobar",
            "display_name": "Novi",
            "password": "SuperSecret123!",
            "role": StaffProfile.KONOBAR,
        })
        created = User.objects.get(username="novikonobar")
        self.assertEqual(created.profile.role, StaffProfile.KONOBAR)

    def test_regular_admin_cannot_tamper_role_to_admin(self):
        """A non-superuser admin's role field is server-side restricted to
        KONOBAR (menu.forms.StaffCreateForm), so even a tampered POST that
        submits role=ADMIN is rejected outright rather than silently
        downgraded — no account should be created at all."""
        self.client.login(username="blerim", password="x")
        self.client.post(reverse("accounts:staff_create"), {
            "username": "tampered",
            "display_name": "Tampered",
            "password": "SuperSecret123!",
            "role": StaffProfile.ADMIN,
        })
        self.assertFalse(User.objects.filter(username="tampered").exists())

    def test_superuser_can_create_admin_role_staff(self):
        self.client.login(username="muhamed", password="x")
        self.client.post(reverse("accounts:staff_create"), {
            "username": "noviadmin",
            "display_name": "Novi Admin",
            "password": "SuperSecret123!",
            "role": StaffProfile.ADMIN,
        })
        created = User.objects.get(username="noviadmin")
        self.assertEqual(created.profile.role, StaffProfile.ADMIN)

    def test_regular_admin_cannot_delete_another_admin(self):
        other_admin = User.objects.create_user("drugiadmin", password="x")
        other_admin.profile.role = StaffProfile.ADMIN
        other_admin.profile.save()

        self.client.login(username="blerim", password="x")
        self.client.post(reverse("accounts:staff_delete", args=[other_admin.id]))
        self.assertTrue(User.objects.filter(pk=other_admin.id).exists())

    def test_superuser_can_delete_regular_admin(self):
        self.client.login(username="muhamed", password="x")
        self.client.post(reverse("accounts:staff_delete", args=[self.admin.id]))
        self.assertFalse(User.objects.filter(pk=self.admin.id).exists())

    def test_cannot_delete_self(self):
        self.client.login(username="blerim", password="x")
        self.client.post(reverse("accounts:staff_delete", args=[self.admin.id]))
        self.assertTrue(User.objects.filter(pk=self.admin.id).exists())

    def test_deleting_waiter_with_order_history_deactivates_instead(self):
        zone = Zone.objects.create(name="Terasa A", order=1)
        table = Table.objects.create(zone=zone, label="A1", order=1)
        Order.objects.create(table=table, waiter=self.konobar)

        self.client.login(username="blerim", password="x")
        self.client.post(reverse("accounts:staff_delete", args=[self.konobar.id]))

        self.konobar.refresh_from_db()
        self.assertTrue(User.objects.filter(pk=self.konobar.id).exists())
        self.assertFalse(self.konobar.is_active)

    def test_deleting_waiter_without_history_removes_them(self):
        self.client.login(username="blerim", password="x")
        self.client.post(reverse("accounts:staff_delete", args=[self.konobar.id]))
        self.assertFalse(User.objects.filter(pk=self.konobar.id).exists())
