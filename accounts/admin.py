from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import StaffProfile


class StaffProfileInline(admin.StackedInline):
    model = StaffProfile
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = [StaffProfileInline]
    list_display = BaseUserAdmin.list_display + ("get_role",)

    @admin.display(description="Roli")
    def get_role(self, obj):
        return getattr(obj, "profile", None) and obj.profile.get_role_display()


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
