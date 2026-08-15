from django.contrib import admin

from .models import Category, MenuItem


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    inlines = [MenuItemInline]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_active", "needs_price_review")
    list_filter = ("category", "is_active", "needs_price_review")
    list_editable = ("price", "is_active")
    search_fields = ("name",)
