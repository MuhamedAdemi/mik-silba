from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("shitje/", views.sales_report, name="sales_report"),
    path("historiku/", views.order_history, name="order_history"),
    path("historiku/<int:order_id>/", views.order_history_detail, name="order_history_detail"),
]
