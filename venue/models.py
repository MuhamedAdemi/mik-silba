from django.db import models


class Zone(models.Model):
    name = models.CharField(max_length=50, unique=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Zonë"
        verbose_name_plural = "Zonat"

    def __str__(self):
        return self.name


class Table(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, related_name="tables")
    label = models.CharField(max_length=20)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["zone__order", "order", "label"]
        unique_together = [("zone", "label")]
        verbose_name = "Tavolinë"
        verbose_name_plural = "Tavolinat"

    def __str__(self):
        return f"{self.zone.name} — {self.label}"

    @property
    def open_order(self):
        """The currently open Order for this table, if any (avoids an app-level
        circular import with `orders` by walking the reverse FK manager)."""
        return self.orders.filter(status="OPEN").order_by("-opened_at").first()

    @property
    def is_occupied(self):
        return self.open_order is not None
