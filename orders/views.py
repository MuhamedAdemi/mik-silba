from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from menu.models import Category, MenuItem
from venue.models import Table, Zone

from .models import CashFloat, Order, OrderItem
from .utils import business_day_bounds, today_business_date


@login_required
@require_POST
def open_table(request, table_id):
    table = get_object_or_404(Table, pk=table_id, is_active=True)
    if table.open_order is None:
        Order.objects.create(table=table, waiter=request.user)
    order = table.open_order
    return redirect("orders:order_detail", order_id=order.id)


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id, status=Order.OPEN)
    categories = Category.objects.prefetch_related("items").filter(
        items__is_active=True
    ).distinct()
    active_category = request.GET.get("kategoria")
    return render(request, "orders/order_detail.html", {
        "order": order,
        "categories": categories,
        "active_category": active_category or (categories.first().id if categories.first() else None),
    })


def _cart_response(request, order):
    return render(request, "orders/_cart.html", {"order": order})


@login_required
@require_POST
def add_item(request, order_id, menu_item_id):
    order = get_object_or_404(Order, pk=order_id, status=Order.OPEN)
    menu_item = get_object_or_404(MenuItem, pk=menu_item_id, is_active=True)
    item, created = OrderItem.objects.get_or_create(
        order=order,
        menu_item=menu_item,
        sent_to_bar_at=None,
        defaults={"quantity": 1, "unit_price": menu_item.price},
    )
    if not created:
        item.quantity += 1
        item.save(update_fields=["quantity"])
    return _cart_response(request, order)


@login_required
@require_POST
def increment_item(request, order_id, item_id):
    order = get_object_or_404(Order, pk=order_id, status=Order.OPEN)
    item = get_object_or_404(OrderItem, pk=item_id, order=order)
    item.quantity += 1
    item.save(update_fields=["quantity"])
    return _cart_response(request, order)


@login_required
@require_POST
def decrement_item(request, order_id, item_id):
    order = get_object_or_404(Order, pk=order_id, status=Order.OPEN)
    item = get_object_or_404(OrderItem, pk=item_id, order=order)
    if item.quantity <= 1:
        item.delete()
    else:
        item.quantity -= 1
        item.save(update_fields=["quantity"])
    return _cart_response(request, order)


@login_required
@require_POST
def remove_item(request, order_id, item_id):
    order = get_object_or_404(Order, pk=order_id, status=Order.OPEN)
    OrderItem.objects.filter(pk=item_id, order=order).delete()
    return _cart_response(request, order)


@login_required
@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id, status=Order.OPEN)
    order.status = Order.CANCELLED
    order.closed_at = timezone.now()
    order.save(update_fields=["status", "closed_at"])
    return redirect("venue:table_grid")


@login_required
def close_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id, status=Order.OPEN)
    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        if payment_method in dict(Order.PAYMENT_CHOICES) and order.items.exists():
            order.status = Order.CLOSED
            order.payment_method = payment_method
            order.closed_at = timezone.now()
            order.save(update_fields=["status", "payment_method", "closed_at"])
            return redirect("orders:print_racun", order_id=order.id)
    return render(request, "orders/close_order.html", {"order": order})


@login_required
def print_shank(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == "POST":
        order.items.filter(sent_to_bar_at__isnull=True).update(sent_to_bar_at=timezone.now())
        return redirect("orders:order_detail", order_id=order.id)
    unsent = order.items.filter(sent_to_bar_at__isnull=True)
    return render(request, "orders/print_shank.html", {"order": order, "items": unsent})


@login_required
def print_predracun(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, "orders/print_predracun.html", {"order": order})


@login_required
def print_racun(request, order_id):
    order = get_object_or_404(Order, pk=order_id, status=Order.CLOSED)
    return render(request, "orders/print_racun.html", {"order": order})


@login_required
def cash_state(request):
    today = today_business_date()

    if request.method == "POST":
        try:
            amount = Decimal(request.POST.get("float_amount", "").replace(",", "."))
        except InvalidOperation:
            amount = None
        if amount is not None and amount >= 0:
            CashFloat.objects.update_or_create(
                waiter=request.user, date=today, defaults={"amount": amount}
            )
        else:
            messages.error(request, "Shuma e pologut nuk është e vlefshme.")
        return redirect("orders:cash_state")

    cash_float = CashFloat.objects.filter(waiter=request.user, date=today).first()

    start, end = business_day_bounds(today)
    orders_today = Order.objects.filter(
        waiter=request.user, status=Order.CLOSED, closed_at__gte=start, closed_at__lt=end
    )
    cash_total = sum((o.total for o in orders_today.filter(payment_method=Order.CASH)), 0)
    card_total = sum((o.total for o in orders_today.filter(payment_method=Order.CARD)), 0)
    eur_total = sum((o.total for o in orders_today.filter(payment_method=Order.EUR)), 0)
    float_amount = cash_float.amount if cash_float else None
    # Both CASH and EUR are physical money in the drawer for now (EUR is a
    # reporting label reserved for a possible future Luceed hand-off, not a
    # different way of taking payment yet).
    expected_drawer = (float_amount + cash_total + eur_total) if float_amount is not None else None

    return render(request, "orders/cash_state.html", {
        "business_date": today,
        "orders_today": orders_today,
        "cash_total": cash_total,
        "card_total": card_total,
        "eur_total": eur_total,
        "grand_total": cash_total + card_total + eur_total,
        "cash_float": cash_float,
        "float_amount": float_amount,
        "expected_drawer": expected_drawer,
    })


@login_required
def move_table_picker(request, order_id):
    order = get_object_or_404(Order, pk=order_id, status=Order.OPEN)
    zones = Zone.objects.prefetch_related("tables").all()
    return render(request, "orders/move_table.html", {"order": order, "zones": zones})


@login_required
@require_POST
def move_table(request, order_id, table_id):
    order = get_object_or_404(Order, pk=order_id, status=Order.OPEN)
    target_table = get_object_or_404(Table, pk=table_id, is_active=True)

    if target_table.id == order.table_id:
        return redirect("orders:order_detail", order_id=order.id)

    if target_table.open_order is not None:
        messages.error(request, f"{target_table.label} është tashmë e zënë.")
        return redirect("orders:move_table_picker", order_id=order.id)

    old_label = order.table.label
    order.table = target_table
    order.save(update_fields=["table"])
    messages.success(request, f"Porosia u zhvendos nga {old_label} te {target_table.label}.")
    return redirect("orders:order_detail", order_id=order.id)
