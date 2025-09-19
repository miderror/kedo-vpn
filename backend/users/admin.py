from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.models import User as AuthUser

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("telegram_id", "username", "referred_by", "date_joined")
    search_fields = ("telegram_id", "username")
    list_filter = ("date_joined",)
    raw_id_fields = ("referred_by",)

    def has_add_permission(self, request):
        return False


admin.site.unregister(AuthUser)
admin.site.unregister(Group)
