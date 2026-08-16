from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.StaffLoginView.as_view(), name="login"),
    path("logout/", views.StaffLogoutView.as_view(), name="logout"),
    path("gjuha/<str:code>/", views.set_language, name="set_language"),
    path("stafi/", views.staff_list, name="staff_list"),
    path("stafi/shto/", views.staff_create, name="staff_create"),
    path("stafi/<int:user_id>/fshi/", views.staff_delete, name="staff_delete"),
]
