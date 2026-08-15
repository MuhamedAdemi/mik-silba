from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("stolovi/", include("orders.urls")),
    path("raporte/", include("reports.urls")),
    path("", include("venue.urls")),
]
