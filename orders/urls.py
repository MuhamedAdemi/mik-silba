from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("tavolina/<int:table_id>/hap/", views.open_table, name="open_table"),
    path("<int:order_id>/", views.order_detail, name="order_detail"),
    path("<int:order_id>/anulo/", views.cancel_order, name="cancel_order"),
    path("<int:order_id>/mbyll/", views.close_order, name="close_order"),
    path("<int:order_id>/artikuj/<int:menu_item_id>/shto/", views.add_item, name="add_item"),
    path("<int:order_id>/artikuj/<int:item_id>/plus/", views.increment_item, name="increment_item"),
    path("<int:order_id>/artikuj/<int:item_id>/minus/", views.decrement_item, name="decrement_item"),
    path("<int:order_id>/artikuj/<int:item_id>/hiq/", views.remove_item, name="remove_item"),
    path("<int:order_id>/print/shank/", views.print_shank, name="print_shank"),
    path("<int:order_id>/print/predracun/", views.print_predracun, name="print_predracun"),
    path("<int:order_id>/print/racun/", views.print_racun, name="print_racun"),
]
