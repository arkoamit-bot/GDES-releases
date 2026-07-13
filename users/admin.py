from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Invitation, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    fields = ["role", "department", "phone", "is_clinician"]
    classes = ["collapse"]


class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = ["username", "email", "first_name", "last_name", "is_staff",
                    "get_role", "date_joined", "last_login"]
    list_filter = UserAdmin.list_filter + ("profile__role", "profile__is_clinician")

    @admin.display(description="Role")
    def get_role(self, obj):
        return obj.profile.get_role_display() if hasattr(obj, "profile") else "—"


# Replace the default User admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ["email", "role", "created_by", "created_at", "used_at", "is_valid"]
    list_filter = ["role", "created_at", "used_at"]
    search_fields = ["email", "token"]
    readonly_fields = ["token", "created_at", "used_at", "used_by"]
    ordering = ["-created_at"]
