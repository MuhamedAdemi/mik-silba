from django.urls import path

from . import views

app_name = "venue"

urlpatterns = [
    path("", views.table_grid, name="table_grid"),
    path("status.json", views.table_status_json, name="table_status_json"),
]
