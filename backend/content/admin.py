from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import BroadcastSettings, SiteSettings


class SingletonModelAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        obj, _ = self.model.objects.get_or_create(pk=1)
        return HttpResponseRedirect(
            reverse(
                f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
                args=(obj.pk,),
            )
        )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonModelAdmin):
    pass


@admin.register(BroadcastSettings)
class BroadcastSettingsAdmin(SingletonModelAdmin):
    raw_id_fields = ("broadcast_admin",)

    class Media:
        css = {"all": ("admin/css/raw_id_fields_fix.css",)}
