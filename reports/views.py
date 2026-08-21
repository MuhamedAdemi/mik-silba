from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Count, DecimalField, F, Sum
from django.db.models.functions import ExtractHour
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from accounts.decorators import admin_required
from orders.models import CashFloat, Order, OrderItem
from orders.utils import business_day_bounds, today_business_date
from venue.models import Zone

User = get_user_model()


def _parse_date(value, default):
    if not value:
        return default
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return default


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
    today = today_business_date()
    date_from = _parse_date(request.GET.get("nga"), today - timedelta(days=7))
    date_to = _parse_date(request.GET.get("deri"), today)

    range_start, _ = business_day_bounds(date_from)
    _, range_end = business_day_bounds(date_to)

    orders_qs = Order.objects.filter(
        status=Order.CLOSED,
        closed_at__gte=range_start,
        closed_at__lt=range_end,
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
        "date_from": date_from.isoformat(),
        "date_to": date_to.isoformat(),
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
    today = today_business_date()
    date_from = _parse_date(request.GET.get("nga"), today)
    date_to = _parse_date(request.GET.get("deri"), today)
    table_query = request.GET.get("stoli", "").strip()

    range_start, _ = business_day_bounds(date_from)
    _, range_end = business_day_bounds(date_to)

    orders = (
        Order.objects.filter(
            status__in=[Order.CLOSED, Order.CANCELLED],
            closed_at__gte=range_start,
            closed_at__lt=range_end,
        )
        .select_related("table", "table__zone", "waiter")
        .order_by("-closed_at")
    )
    if table_query:
        orders = orders.filter(table__label__icontains=table_query)

    return render(request, "reports/order_history.html", {
        "orders": orders,
        "date_from": date_from.isoformat(),
        "date_to": date_to.isoformat(),
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


@admin_required
def cash_overview(request):
    today = today_business_date()
    selected_date = _parse_date(request.GET.get("data"), today)
    start, end = business_day_bounds(selected_date)

    orders_qs = Order.objects.filter(status=Order.CLOSED, closed_at__gte=start, closed_at__lt=end)
    waiters = User.objects.filter(orders__in=orders_qs).select_related("profile").distinct()
    floats_by_waiter = {
        f.waiter_id: f.amount
        for f in CashFloat.objects.filter(date=selected_date, waiter__in=waiters)
    }

    rows = []
    grand_cash = grand_card = grand_eur = grand_float = Decimal("0")
    for waiter in waiters:
        waiter_orders = orders_qs.filter(waiter=waiter)
        cash = sum((o.total for o in waiter_orders.filter(payment_method=Order.CASH)), Decimal("0"))
        card = sum((o.total for o in waiter_orders.filter(payment_method=Order.CARD)), Decimal("0"))
        eur = sum((o.total for o in waiter_orders.filter(payment_method=Order.EUR)), Decimal("0"))
        float_amount = floats_by_waiter.get(waiter.id, Decimal("0"))
        rows.append({
            "waiter": waiter,
            "float": float_amount,
            "cash": cash,
            "card": card,
            "eur": eur,
            "expected_drawer": float_amount + cash + eur,
        })
        grand_cash += cash
        grand_card += card
        grand_eur += eur
        grand_float += float_amount

    rows.sort(key=lambda r: r["waiter"].profile.display_name or r["waiter"].username)

    return render(request, "reports/cash_overview.html", {
        "selected_date": selected_date,
        "prev_date": selected_date - timedelta(days=1),
        "next_date": selected_date + timedelta(days=1),
        "today": today,
        "rows": rows,
        "grand_float": grand_float,
        "grand_cash": grand_cash,
        "grand_card": grand_card,
        "grand_eur": grand_eur,
        "grand_expected": grand_float + grand_cash + grand_eur,
        "grand_total": grand_cash + grand_card + grand_eur,
    })
