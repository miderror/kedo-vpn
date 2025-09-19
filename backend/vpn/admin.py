from django.contrib import admin

from .models import Subscription, Tariff


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ("name", "duration_days", "price", "is_active", "order")
    list_editable = ("is_active", "order")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "end_date", "is_active", "total_paid", "trial_activated")
    search_fields = ("user__telegram_id", "user__username")
    list_filter = ("end_date", "trial_activated")
    readonly_fields = ("vless_uuid",)

    @admin.display(boolean=True, description="Активна")
    def is_active(self, obj):
        return obj.is_active
