from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoritë"

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="items")
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    needs_price_review = models.BooleanField(
        default=False,
        help_text="Çmimi nuk ishte i lexueshëm/i sigurt nga fotot — kontrollo dhe korrigjo.",
    )

    class Meta:
        ordering = ["category__order", "sort_order", "name"]
        unique_together = [("category", "name")]
        verbose_name = "Artikull"
        verbose_name_plural = "Artikujt"

    def __str__(self):
        return f"{self.name} ({self.price} €)"
