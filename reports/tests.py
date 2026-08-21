from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import StaffProfile
from menu.models import Category, MenuItem
from orders.models import CashFloat, Order, OrderItem
from orders.utils import business_day_bounds, today_business_date
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


class CashOverviewTests(TestCase):
    def setUp(self):
        self.konobar1 = User.objects.create_user("konobar1", password="pass12345")
        self.konobar2 = User.objects.create_user("konobar2", password="pass12345")
        self.admin = User.objects.create_user("shefi1", password="pass12345")
        self.admin.profile.role = StaffProfile.ADMIN
        self.admin.profile.save()

        zone = Zone.objects.create(name="Terasa A", order=1)
        self.table = Table.objects.create(zone=zone, label="A1", order=1)
        category = Category.objects.create(name="Napici+Sok", order=1)
        self.item = MenuItem.objects.create(category=category, name="Cappuccino", price=Decimal("2.30"))

        self.today = today_business_date()
        start, _ = business_day_bounds(self.today)
        within_day = start + timedelta(hours=1)

        CashFloat.objects.create(waiter=self.konobar1, date=self.today, amount=Decimal("100"))
        CashFloat.objects.create(waiter=self.konobar2, date=self.today, amount=Decimal("50"))

        order1 = Order.objects.create(
            table=self.table, waiter=self.konobar1, status=Order.CLOSED,
            payment_method=Order.CASH, closed_at=within_day,
        )
        OrderItem.objects.create(order=order1, menu_item=self.item, quantity=1, unit_price=Decimal("2.30"))

        order2 = Order.objects.create(
            table=self.table, waiter=self.konobar2, status=Order.CLOSED,
            payment_method=Order.CARD, closed_at=within_day,
        )
        OrderItem.objects.create(order=order2, menu_item=self.item, quantity=2, unit_price=Decimal("2.30"))

        self.client.login(username="shefi1", password="pass12345")

    def test_konobar_cannot_access_cash_overview(self):
        self.client.logout()
        self.client.login(username="konobar1", password="pass12345")
        response = self.client.get(reverse("reports:cash_overview"))
        self.assertEqual(response.status_code, 403)

    def test_shows_all_waiters_for_the_day_combined(self):
        response = self.client.get(reverse("reports:cash_overview"))
        self.assertEqual(response.status_code, 200)
        rows_by_waiter = {row["waiter"].username: row for row in response.context["rows"]}
        self.assertEqual(rows_by_waiter["konobar1"]["cash"], Decimal("2.30"))
        self.assertEqual(rows_by_waiter["konobar1"]["float"], Decimal("100"))
        self.assertEqual(rows_by_waiter["konobar1"]["expected_drawer"], Decimal("102.30"))
        self.assertEqual(rows_by_waiter["konobar2"]["card"], Decimal("4.60"))

    def test_grand_totals_sum_across_waiters(self):
        response = self.client.get(reverse("reports:cash_overview"))
        self.assertEqual(response.context["grand_cash"], Decimal("2.30"))
        self.assertEqual(response.context["grand_card"], Decimal("4.60"))
        self.assertEqual(response.context["grand_float"], Decimal("150"))

    def test_navigating_to_a_day_with_no_sales_shows_empty(self):
        far_future = (self.today + timedelta(days=365)).isoformat()
        response = self.client.get(reverse("reports:cash_overview"), {"data": far_future})
        self.assertEqual(len(response.context["rows"]), 0)

    def test_eur_payments_shown_and_included_in_grand_totals(self):
        start, _ = business_day_bounds(self.today)
        within_day = start + timedelta(hours=1)
        eur_order = Order.objects.create(
            table=self.table, waiter=self.konobar1, status=Order.CLOSED,
            payment_method=Order.EUR, closed_at=within_day,
        )
        OrderItem.objects.create(order=eur_order, menu_item=self.item, quantity=1, unit_price=Decimal("2.30"))

        response = self.client.get(reverse("reports:cash_overview"))
        rows_by_waiter = {row["waiter"].username: row for row in response.context["rows"]}
        self.assertEqual(rows_by_waiter["konobar1"]["eur"], Decimal("2.30"))
        self.assertEqual(response.context["grand_eur"], Decimal("2.30"))
        self.assertEqual(response.context["grand_total"], Decimal("9.20"))
