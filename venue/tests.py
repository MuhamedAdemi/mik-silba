from django.contrib.auth.models import User
from django.test import TestCase

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
