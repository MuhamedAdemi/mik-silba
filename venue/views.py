from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from .models import Zone


@login_required
def table_grid(request):
    zones = Zone.objects.prefetch_related("tables").all()
    return render(request, "venue/table_grid.html", {"zones": zones})


@login_required
def table_status_json(request):
    now = timezone.now()
    data = {}
    for zone in Zone.objects.prefetch_related("tables__orders"):
        for table in zone.tables.all():
            order = table.open_order
            if order:
                minutes = int((now - order.opened_at).total_seconds() // 60)
                data[table.id] = {
                    "occupied": True,
                    "minutes_open": minutes,
                    "total": str(order.total),
                    "waiter": order.waiter.get_username() if order.waiter else "",
                }
            else:
                data[table.id] = {"occupied": False}
    return JsonResponse({"tables": data, "server_time": now.isoformat()})
