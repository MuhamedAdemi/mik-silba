from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("added_at", "sent_to_bar_at")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "table", "waiter", "status", "payment_method", "opened_at", "closed_at", "total")
    list_filter = ("status", "payment_method", "table__zone")
    date_hierarchy = "opened_at"
    inlines = [OrderItemInline]
    readonly_fields = ("opened_at",)
