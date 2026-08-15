from django.contrib import admin

from .models import Table, Zone


class TableInline(admin.TabularInline):
    model = Table
    extra = 1


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    inlines = [TableInline]


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("label", "zone", "is_active", "order")
    list_filter = ("zone", "is_active")
    search_fields = ("label",)
