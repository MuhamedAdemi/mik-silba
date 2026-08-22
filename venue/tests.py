from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from orders.models import Order
from .models import Table, Zone


class TableOccupancyTests(TestCase):
    def setUp(self):
        self.zone = Zone.objects.create(name="Terasa A", order=1)
        self.table = Table.objects.create(zone=self.zone, label="A1", order=1)
        self.waiter = User.objects.create_user("konobar1", password="x")

    def test_free_table_has_no_open_order(self):
        self.assertFalse(self.table.is_occupied)
        self.assertIsNone(self.table.open_order)

    def test_table_occupied_while_order_open(self):
        order = Order.objects.create(table=self.table, waiter=self.waiter)
        self.assertTrue(self.table.is_occupied)
        self.assertEqual(self.table.open_order, order)

    def test_table_free_again_after_order_closed(self):
        order = Order.objects.create(table=self.table, waiter=self.waiter)
        order.status = Order.CLOSED
        order.save()
        self.assertFalse(self.table.is_occupied)


class TableGridMoveHandleTests(TestCase):
    """The in-grid quick-move affordance (⇄ icon + micStartMove) only makes
    sense — and should only render — on tables that actually have an open
    order to move."""

    def setUp(self):
        zone = Zone.objects.create(name="Terasa A", order=1)
        self.free_table = Table.objects.create(zone=zone, label="A1", order=1)
        self.occupied_table = Table.objects.create(zone=zone, label="A2", order=2)
        self.waiter = User.objects.create_user("konobar1", password="pass12345")
        self.order = Order.objects.create(table=self.occupied_table, waiter=self.waiter)
        self.client.login(username="konobar1", password="pass12345")

    def test_move_handle_rendered_only_for_occupied_table(self):
        response = self.client.get(reverse("venue:table_grid"))
        self.assertContains(response, f"micStartMove({self.order.id}, 'A2')")
        self.assertNotContains(response, "micStartMove(None")

    def test_free_table_form_carries_move_submit_guard(self):
        response = self.client.get(reverse("venue:table_grid"))
        self.assertContains(response, f"micFreeTableSubmit(event, {self.free_table.id})")
