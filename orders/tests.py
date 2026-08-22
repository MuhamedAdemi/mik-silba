from datetime import date, datetime, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from menu.models import Category, MenuItem
from venue.models import Table, Zone

from .models import CashFloat, Order, OrderItem
from .utils import business_date, business_day_bounds, today_business_date


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

    def test_print_shank_marks_items_sent(self):
        self.client.post(reverse("orders:open_table", args=[self.table.id]))
        order = self.table.open_order
        self.client.post(reverse("orders:add_item", args=[order.id, self.item.id]))
        self.client.post(reverse("orders:print_shank", args=[order.id]))
        order_item = OrderItem.objects.get(order=order, menu_item=self.item)
        self.assertIsNotNone(order_item.sent_to_bar_at)


class CloseOrderConfirmTests(TestCase):
    """Closing a table is two phases: picking a payment method only opens a
    review screen (order stays OPEN, table stays occupied); only POSTing to
    that review screen actually closes the order and frees the table. This
    lets staff show the bill on a phone without printing, and back out
    without any state change if the guest isn't ready yet."""

    def setUp(self):
        zone = Zone.objects.create(name="Terasa A", order=1)
        self.table = Table.objects.create(zone=zone, label="A1", order=1)
        self.waiter = User.objects.create_user("konobar1", password="pass12345")
        category = Category.objects.create(name="Napici+Sok", order=1)
        self.item = MenuItem.objects.create(category=category, name="Cappuccino", price=Decimal("2.50"))
        self.client.login(username="konobar1", password="pass12345")
        self.client.post(reverse("orders:open_table", args=[self.table.id]))
        self.order = self.table.open_order
        self.client.post(reverse("orders:add_item", args=[self.order.id, self.item.id]))

    def test_viewing_confirm_screen_does_not_close_the_order(self):
        response = self.client.get(reverse("orders:close_order_confirm", args=[self.order.id]), {"metode": "CARD"})
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.OPEN)
        self.assertTrue(self.table.is_occupied)
        self.assertContains(response, "Cappuccino")

    def test_confirming_closes_order_and_frees_table(self):
        response = self.client.post(
            reverse("orders:close_order_confirm", args=[self.order.id]), {"payment_method": "CARD"}
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.CLOSED)
        self.assertEqual(self.order.payment_method, Order.CARD)
        self.assertFalse(self.table.is_occupied)
        self.assertRedirects(response, reverse("orders:print_racun", args=[self.order.id]))

    def test_confirming_accepts_eur_payment_method(self):
        self.client.post(reverse("orders:close_order_confirm", args=[self.order.id]), {"payment_method": "EUR"})
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_method, Order.EUR)

    def test_invalid_payment_method_redirects_to_chooser(self):
        response = self.client.get(reverse("orders:close_order_confirm", args=[self.order.id]), {"metode": "BITCOIN"})
        self.assertRedirects(response, reverse("orders:close_order", args=[self.order.id]))

    def test_cannot_confirm_close_without_items(self):
        empty_order = self.table.open_order
        OrderItem.objects.filter(order=empty_order).delete()
        response = self.client.post(
            reverse("orders:close_order_confirm", args=[empty_order.id]), {"payment_method": "CASH"}
        )
        empty_order.refresh_from_db()
        self.assertEqual(empty_order.status, Order.OPEN)
        self.assertRedirects(response, reverse("orders:close_order", args=[empty_order.id]))


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
        today = today_business_date()
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
        today = today_business_date()
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
        today = today_business_date()
        self.assertEqual(CashFloat.objects.filter(waiter=self.waiter, date=today).count(), 1)
        self.assertEqual(CashFloat.objects.get(waiter=self.waiter, date=today).amount, Decimal("150"))

    def test_invalid_float_amount_is_rejected(self):
        self.client.post(reverse("orders:cash_state"), {"float_amount": "abc"})
        today = today_business_date()
        self.assertFalse(CashFloat.objects.filter(waiter=self.waiter, date=today).exists())

    def test_eur_payments_are_tracked_separately_but_count_toward_drawer(self):
        eur_order = Order.objects.create(
            table=self.table, waiter=self.waiter, status=Order.CLOSED,
            payment_method=Order.EUR, closed_at=timezone.now(),
        )
        category = Category.objects.create(name="Pivo+Vino", order=2)
        item = MenuItem.objects.create(category=category, name="Karlovačko", price=Decimal("3.00"))
        OrderItem.objects.create(order=eur_order, menu_item=item, quantity=1, unit_price=Decimal("3.00"))

        self.client.post(reverse("orders:cash_state"), {"float_amount": "100"})
        response = self.client.get(reverse("orders:cash_state"))

        self.assertEqual(response.context["eur_total"], Decimal("3.00"))
        self.assertEqual(response.context["cash_total"], Decimal("4.60"))
        # expected drawer = float + cash + eur = 100 + 4.60 + 3.00
        self.assertEqual(response.context["expected_drawer"], Decimal("107.60"))
        self.assertEqual(response.context["grand_total"], Decimal("7.60"))


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


class BusinessDayTests(TestCase):
    """Caffe MiK stays open from ~08:00 to ~03:00 the next calendar day, so
    the 'business day' boundary is 07:00, not midnight (see orders/utils.py
    and settings.BUSINESS_DAY_CUTOFF_HOUR)."""

    def test_late_night_sale_belongs_to_previous_calendar_days_business_day(self):
        late_night = timezone.make_aware(datetime(2026, 3, 15, 1, 30))
        self.assertEqual(business_date(late_night), date(2026, 3, 14))

    def test_mid_afternoon_sale_belongs_to_same_calendar_days_business_day(self):
        afternoon = timezone.make_aware(datetime(2026, 3, 15, 15, 0))
        self.assertEqual(business_date(afternoon), date(2026, 3, 15))

    def test_exactly_at_cutoff_belongs_to_that_calendar_day(self):
        at_cutoff = timezone.make_aware(datetime(2026, 3, 15, 7, 0))
        self.assertEqual(business_date(at_cutoff), date(2026, 3, 15))

    def test_business_day_bounds_span_cutoff_to_cutoff(self):
        start, end = business_day_bounds(date(2026, 3, 15))
        self.assertEqual(start, timezone.make_aware(datetime(2026, 3, 15, 7, 0)))
        self.assertEqual(end, timezone.make_aware(datetime(2026, 3, 16, 7, 0)))

    def test_cash_state_only_counts_sales_within_current_business_day_bounds(self):
        waiter = User.objects.create_user("konobar9", password="pass12345")
        zone = Zone.objects.create(name="Terasa A", order=1)
        table = Table.objects.create(zone=zone, label="A1", order=1)
        category = Category.objects.create(name="Napici+Sok", order=1)
        item = MenuItem.objects.create(category=category, name="Cappuccino", price=Decimal("2.30"))

        start, _ = business_day_bounds(today_business_date())
        # Any timestamp inside [start, start+24h) belongs to today's business
        # day regardless of what wall-clock time this test happens to run at.
        within_business_day = start + timedelta(hours=1)

        order = Order.objects.create(
            table=table, waiter=waiter, status=Order.CLOSED,
            payment_method=Order.CASH, closed_at=within_business_day,
        )
        OrderItem.objects.create(order=order, menu_item=item, quantity=1, unit_price=Decimal("2.30"))

        # Just before the cutoff -> belongs to the *previous* business day,
        # should NOT show up in today's Stanje kase.
        before_cutoff = start - timedelta(minutes=5)
        other_order = Order.objects.create(
            table=table, waiter=waiter, status=Order.CLOSED,
            payment_method=Order.CASH, closed_at=before_cutoff,
        )
        OrderItem.objects.create(order=other_order, menu_item=item, quantity=1, unit_price=Decimal("2.30"))

        client = Client()
        client.login(username="konobar9", password="pass12345")
        response = client.get(reverse("orders:cash_state"))
        self.assertEqual(response.context["cash_total"], Decimal("2.30"))
