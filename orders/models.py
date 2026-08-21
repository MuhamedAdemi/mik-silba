from decimal import Decimal

from django.conf import settings
from django.db import models


class Order(models.Model):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"
    STATUS_CHOICES = [
        (OPEN, "Hapur"),
        (CLOSED, "Mbyllur"),
        (CANCELLED, "Anuluar"),
    ]

    CASH = "CASH"
    CARD = "CARD"
    EUR = "EUR"
    PAYMENT_CHOICES = [
        (CASH, "Gotovina"),
        (CARD, "Kartica"),
        (EUR, "Eur"),
    ]

    table = models.ForeignKey(
        "venue.Table", on_delete=models.PROTECT, related_name="orders"
    )
    waiter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders"
    )
    guest_note = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=OPEN)
    payment_method = models.CharField(
        max_length=10, choices=PAYMENT_CHOICES, blank=True
    )
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-opened_at"]
        verbose_name = "Porosi"
        verbose_name_plural = "Porositë"

    def __str__(self):
        return f"{self.table} — {self.get_status_display()}"

    @property
    def total(self):
        return sum(
            (item.quantity * item.unit_price for item in self.items.all()),
            Decimal("0.00"),
        )

    @property
    def has_unsent_items(self):
        return self.items.filter(sent_to_bar_at__isnull=True).exists()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(
        "menu.MenuItem", on_delete=models.PROTECT, related_name="order_items"
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)
    sent_to_bar_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["added_at"]
        verbose_name = "Artikull i porosisë"
        verbose_name_plural = "Artikujt e porosisë"

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"

    @property
    def subtotal(self):
        return self.quantity * self.unit_price


class CashFloat(models.Model):
    """The starting cash amount ('polog') a waiter puts in the drawer at the
    start of their shift, so Stanje kase can show the expected cash-in-drawer
    total (float + cash sales) alongside card sales, for end-of-shift counting."""

    waiter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cash_floats"
    )
    date = models.DateField()
    amount = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal("100.00"))
    set_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("waiter", "date")]
        verbose_name = "Polog"
        verbose_name_plural = "Pologjet"

    def __str__(self):
        return f"{self.waiter} — {self.date} — {self.amount}"
