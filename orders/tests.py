from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from menu.models import Category, MenuItem
from venue.models import Table, Zone

from .models import CashFloat, Order, OrderItem


class OrderModelTests(TestCase):
    def setUp(self):
        zone = Zone.objects.create(name="Terasa A", order=1)
        self.table = Table.objects.create(zone=zone, label="A1", order=1)
        self.waiter = User.objects.create_user("konobar1", password="x")
        self.order = Order.objects.create(table=self.table, waiter=self.waiter)
        category = Category.objects.create(name="Napici+Sok", order=1)
        self.item = MenuItem.objects.create(category=category, name="Cappuccino", price=Decimal("2.50"))

    def test_total_sums_order_items(self):
        OrderItem.objects.create(order=self.order, menu_item=self.item, quantity=2, unit_price=Decimal("2.50"))
        self.assertEqual(self.order.total, Decimal("5.00"))

    def test_total_zero_with_no_items(self):
        self.assertEqual(self.order.total, Decimal("0.00"))


class OrderFlowViewTests(TestCase):
    def setUp(self):
        zone = Zone.objects.create(name="Terasa A", order=1)
        self.table = Table.objects.create(zone=zone, label="A1", order=1)
        self.waiter = User.objects.create_user("konobar1", password="pass12345")
        category = Category.objects.create(name="Napici+Sok", order=1)
        self.item = MenuItem.objects.create(category=category, name="Cappuccino", price=Decimal("2.50"))
        self.client.login(username="konobar1", password="pass12345")

    def test_open_table_creates_order_and_is_idempotent(self):
        url = reverse("orders:open_table", args=[self.table.id])
        self.client.post(url)
        self.assertEqual(Order.objects.filter(table=self.table, status=Order.OPEN).count(), 1)
        self.client.post(url)
        self.assertEqual(Order.objects.filter(table=self.table, status=Order.OPEN).count(), 1)

    def test_add_item_twice_increments_quantity(self):
        self.client.post(reverse("orders:open_table", args=[self.table.id]))
        order = self.table.open_order
        add_url = reverse("orders:add_item", args=[order.id, self.item.id])
        self.client.post(add_url)
        self.client.post(add_url)
        order_item = OrderItem.objects.get(order=order, menu_item=self.item)
        self.assertEqual(order_item.quantity, 2)

    def test_cannot_close_order_without_items(self):
        self.client.post(reverse("orders:open_table", args=[self.table.id]))
        order = self.table.open_order
        response = self.client.post(reverse("orders:close_order", args=[order.id]), {"payment_method": "CASH"})
        order.refresh_from_db()
        self.assertEqual(order.status, Order.OPEN)
        self.assertEqual(response.status_code, 200)

    def test_close_order_with_items_frees_table(self):
        self.client.post(reverse("orders:open_table", args=[self.table.id]))
        order = self.table.open_order
        self.client.post(reverse("orders:add_item", args=[order.id, self.item.id]))
        response = self.client.post(reverse("orders:close_order", args=[order.id]), {"payment_method": "CARD"})
        order.refresh_from_db()
        self.assertEqual(order.status, Order.CLOSED)
        self.assertEqual(order.payment_method, Order.CARD)
        self.assertFalse(self.table.is_occupied)
        self.assertRedirects(response, reverse("orders:print_racun", args=[order.id]))

    def test_print_shank_marks_items_sent(self):
        self.client.post(reverse("orders:open_table", args=[self.table.id]))
        order = self.table.open_order
        self.client.post(reverse("orders:add_item", args=[order.id, self.item.id]))
        self.client.post(reverse("orders:print_shank", args=[order.id]))
        order_item = OrderItem.objects.get(order=order, menu_item=self.item)
        self.assertIsNotNone(order_item.sent_to_bar_at)


class HtmxCsrfTests(TestCase):
    """Regression test: the real browser (htmx) sends the CSRF token via the
    X-CSRFToken header, set globally through hx-headers on <body> in
    base.html (see templates/base.html). Django's default test Client skips
    CSRF checks entirely, which is why this class of bug wasn't caught by
    the other view tests — this one turns CSRF enforcement back on."""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        zone = Zone.objects.create(name="Terasa A", order=1)
        self.table = Table.objects.create(zone=zone, label="A1", order=1)
        User.objects.create_user("konobar1", password="pass12345")
        self.client.login(username="konobar1", password="pass12345")
        category = Category.objects.create(name="Napici+Sok", order=1)
        self.item = MenuItem.objects.create(category=category, name="Cappuccino", price=Decimal("2.50"))

        # A real GET (unlike Client.login()) renders {% csrf_token %} and sets
        # the csrftoken cookie, exactly like a browser loading the page first.
        self.client.get(reverse("venue:table_grid"))
        csrf_token = self.client.cookies["csrftoken"].value
        self.client.post(
            reverse("orders:open_table", args=[self.table.id]),
            {"csrfmiddlewaretoken": csrf_token},
        )
        self.order = self.table.open_order

    def test_add_item_without_csrf_header_is_rejected(self):
        response = self.client.post(reverse("orders:add_item", args=[self.order.id, self.item.id]))
        self.assertEqual(response.status_code, 403)

    def test_add_item_with_csrf_header_succeeds(self):
        csrf_token = self.client.cookies["csrftoken"].value
        response = self.client.post(
            reverse("orders:add_item", args=[self.order.id, self.item.id]),
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(OrderItem.objects.filter(order=self.order, menu_item=self.item).exists())


class CashStateTests(TestCase):
    def setUp(self):
        self.waiter = User.objects.create_user("konobar1", password="pass12345")
        zone = Zone.objects.create(name="Terasa A", order=1)
        self.table = Table.objects.create(zone=zone, label="A1", order=1)
        today = timezone.localdate()
        self.cash_order = Order.objects.create(
            table=self.table, waiter=self.waiter, status=Order.CLOSED,
            payment_method=Order.CASH, closed_at=timezone.now(),
        )
        category = Category.objects.create(name="Napici+Sok", order=1)
        item = MenuItem.objects.create(category=category, name="Cappuccino", price=Decimal("2.30"))
        OrderItem.objects.create(order=self.cash_order, menu_item=item, quantity=2, unit_price=Decimal("2.30"))
        self.client.login(username="konobar1", password="pass12345")

    def test_no_float_set_shows_prompt_and_no_expected_drawer(self):
        response = self.client.get(reverse("orders:cash_state"))
        self.assertIsNone(response.context["cash_float"])
        self.assertIsNone(response.context["expected_drawer"])

    def test_setting_float_creates_record_for_today(self):
        self.client.post(reverse("orders:cash_state"), {"float_amount": "100"})
        today = timezone.localdate()
        cash_float = CashFloat.objects.get(waiter=self.waiter, date=today)
        self.assertEqual(cash_float.amount, Decimal("100"))

    def test_expected_drawer_is_float_plus_cash_sales(self):
        self.client.post(reverse("orders:cash_state"), {"float_amount": "100"})
        response = self.client.get(reverse("orders:cash_state"))
        # 2 x 2.30 = 4.60 cash sales + 100 float
        self.assertEqual(response.context["expected_drawer"], Decimal("104.60"))
        self.assertEqual(response.context["cash_total"], Decimal("4.60"))

    def test_updating_float_overwrites_same_day_record(self):
        self.client.post(reverse("orders:cash_state"), {"float_amount": "100"})
        self.client.post(reverse("orders:cash_state"), {"float_amount": "150"})
        today = timezone.localdate()
        self.assertEqual(CashFloat.objects.filter(waiter=self.waiter, date=today).count(), 1)
        self.assertEqual(CashFloat.objects.get(waiter=self.waiter, date=today).amount, Decimal("150"))

    def test_invalid_float_amount_is_rejected(self):
        self.client.post(reverse("orders:cash_state"), {"float_amount": "abc"})
        today = timezone.localdate()
        self.assertFalse(CashFloat.objects.filter(waiter=self.waiter, date=today).exists())


class MoveTableTests(TestCase):
    def setUp(self):
        self.waiter = User.objects.create_user("konobar1", password="pass12345")
        zone = Zone.objects.create(name="Terasa A", order=1)
        self.table_a1 = Table.objects.create(zone=zone, label="A1", order=1)
        self.table_a2 = Table.objects.create(zone=zone, label="A2", order=2)
        self.order = Order.objects.create(table=self.table_a1, waiter=self.waiter)
        category = Category.objects.create(name="Napici+Sok", order=1)
        item = MenuItem.objects.create(category=category, name="Cappuccino", price=Decimal("2.50"))
        OrderItem.objects.create(order=self.order, menu_item=item, quantity=1, unit_price=Decimal("2.50"))
        self.client.login(username="konobar1", password="pass12345")

    def test_move_to_free_table_updates_order_and_frees_old_table(self):
        response = self.client.post(reverse("orders:move_table", args=[self.order.id, self.table_a2.id]))
        self.order.refresh_from_db()
        self.assertEqual(self.order.table_id, self.table_a2.id)
        self.assertFalse(self.table_a1.is_occupied)
        self.assertRedirects(response, reverse("orders:order_detail", args=[self.order.id]))

    def test_move_preserves_order_items(self):
        self.client.post(reverse("orders:move_table", args=[self.order.id, self.table_a2.id]))
        self.order.refresh_from_db()
        self.assertEqual(self.order.items.count(), 1)
        self.assertEqual(self.order.total, Decimal("2.50"))

    def test_cannot_move_to_occupied_table(self):
        other_waiter = User.objects.create_user("konobar2", password="x")
        Order.objects.create(table=self.table_a2, waiter=other_waiter)

        self.client.post(reverse("orders:move_table", args=[self.order.id, self.table_a2.id]))
        self.order.refresh_from_db()
        self.assertEqual(self.order.table_id, self.table_a1.id)

    def test_move_picker_shows_current_table_and_free_tables(self):
        response = self.client.get(reverse("orders:move_table_picker", args=[self.order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A1")
        self.assertContains(response, "A2")
