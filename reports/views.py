from datetime import timedelta

from django.db.models import Count, DecimalField, F, Sum
from django.db.models.functions import ExtractHour
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from accounts.decorators import admin_required
from orders.models import Order, OrderItem
from venue.models import Zone


@admin_required
def dashboard(request):
    now = timezone.now()
    open_orders = list(
        Order.objects.filter(status=Order.OPEN)
        .select_related("table", "table__zone", "waiter")
        .order_by("opened_at")
    )
    for order in open_orders:
        order.minutes_open = int((now - order.opened_at).total_seconds() // 60)

    zone_stats = []
    for zone in Zone.objects.prefetch_related("tables"):
        tables = list(zone.tables.filter(is_active=True))
        occupied = sum(1 for t in tables if t.is_occupied)
        zone_stats.append({"zone": zone, "occupied": occupied, "total": len(tables)})

    return render(request, "reports/dashboard.html", {
        "zone_stats": zone_stats,
        "open_orders": open_orders,
    })


@admin_required
def sales_report(request):
    today = timezone.localdate()
    date_from = request.GET.get("nga") or (today - timedelta(days=7)).isoformat()
    date_to = request.GET.get("deri") or today.isoformat()

    orders_qs = Order.objects.filter(
        status=Order.CLOSED,
        closed_at__date__gte=date_from,
        closed_at__date__lte=date_to,
    )
    items_qs = OrderItem.objects.filter(order__in=orders_qs)
    revenue_expr = Sum(F("quantity") * F("unit_price"), output_field=DecimalField())

    total_revenue = items_qs.aggregate(total=revenue_expr)["total"] or 0
    orders_count = orders_qs.count()

    top_items = (
        items_qs.values("menu_item__name")
        .annotate(qty=Sum("quantity"), revenue=revenue_expr)
        .order_by("-revenue")[:10]
    )

    by_category = (
        items_qs.values("menu_item__category__name")
        .annotate(revenue=revenue_expr)
        .order_by("-revenue")
    )

    by_waiter = (
        orders_qs.values("waiter__username")
        .annotate(
            revenue=Sum(F("items__quantity") * F("items__unit_price"), output_field=DecimalField()),
            orders=Count("id", distinct=True),
        )
        .order_by("-revenue")
    )

    busy_hours = (
        items_qs.annotate(hour=ExtractHour("added_at"))
        .values("hour")
        .annotate(qty=Sum("quantity"))
    )
    busy_hours_map = {row["hour"]: row["qty"] for row in busy_hours}
    busy_hours_chart = [busy_hours_map.get(h, 0) for h in range(24)]

    return render(request, "reports/sales_report.html", {
        "date_from": date_from,
        "date_to": date_to,
        "total_revenue": total_revenue,
        "orders_count": orders_count,
        "top_items": top_items,
        "by_category": by_category,
        "by_waiter": by_waiter,
        "busy_hours_chart": busy_hours_chart,
        "busy_hours_labels": list(range(24)),
    })


@admin_required
def order_history(request):
    today = timezone.localdate().isoformat()
    date_from = request.GET.get("nga") or today
    date_to = request.GET.get("deri") or today
    table_query = request.GET.get("stoli", "").strip()

    orders = (
        Order.objects.filter(
            status__in=[Order.CLOSED, Order.CANCELLED],
            closed_at__date__gte=date_from,
            closed_at__date__lte=date_to,
        )
        .select_related("table", "table__zone", "waiter")
        .order_by("-closed_at")
    )
    if table_query:
        orders = orders.filter(table__label__icontains=table_query)

    return render(request, "reports/order_history.html", {
        "orders": orders,
        "date_from": date_from,
        "date_to": date_to,
        "table_query": table_query,
    })


@admin_required
def order_history_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related("table", "table__zone", "waiter"),
        pk=order_id,
        status__in=[Order.CLOSED, Order.CANCELLED],
    )
    return render(request, "reports/order_history_detail.html", {"order": order})
