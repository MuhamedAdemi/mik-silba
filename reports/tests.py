from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import StaffProfile
from menu.models import Category, MenuItem
from orders.models import Order, OrderItem
from venue.models import Table, Zone


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


class OrderHistoryTests(TestCase):
    def setUp(self):
        self.konobar = User.objects.create_user("konobar1", password="pass12345")
        self.admin = User.objects.create_user("shefi1", password="pass12345")
        self.admin.profile.role = StaffProfile.ADMIN
        self.admin.profile.save()

        zone = Zone.objects.create(name="Terasa A", order=1)
        self.table_a1 = Table.objects.create(zone=zone, label="A1", order=1)
        self.table_a2 = Table.objects.create(zone=zone, label="A2", order=2)
        category = Category.objects.create(name="Napici+Sok", order=1)
        self.item = MenuItem.objects.create(category=category, name="Cappuccino", price=Decimal("2.30"))

        now = timezone.now()
        self.closed_order = Order.objects.create(
            table=self.table_a1, waiter=self.konobar, status=Order.CLOSED,
            payment_method=Order.CARD, closed_at=now,
        )
        OrderItem.objects.create(
            order=self.closed_order, menu_item=self.item, quantity=2, unit_price=Decimal("2.30")
        )
        self.cancelled_order = Order.objects.create(
            table=self.table_a2, waiter=self.konobar, status=Order.CANCELLED, closed_at=now,
        )

    def test_konobar_cannot_access_history(self):
        self.client.login(username="konobar1", password="pass12345")
        response = self.client.get(reverse("reports:order_history"))
        self.assertEqual(response.status_code, 403)

    def test_admin_sees_closed_and_cancelled_orders_today(self):
        self.client.login(username="shefi1", password="pass12345")
        response = self.client.get(reverse("reports:order_history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A1")
        self.assertContains(response, "A2")

    def test_filter_by_table_label(self):
        self.client.login(username="shefi1", password="pass12345")
        response = self.client.get(reverse("reports:order_history"), {"stoli": "A1"})
        self.assertContains(response, "A1")
        self.assertNotContains(response, "A2")

    def test_history_detail_shows_items(self):
        self.client.login(username="shefi1", password="pass12345")
        response = self.client.get(reverse("reports:order_history_detail", args=[self.closed_order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cappuccino")

    def test_open_order_not_reachable_via_history_detail(self):
        open_order = Order.objects.create(table=self.table_a1, waiter=self.konobar)
        self.client.login(username="shefi1", password="pass12345")
        response = self.client.get(reverse("reports:order_history_detail", args=[open_order.id]))
        self.assertEqual(response.status_code, 404)
