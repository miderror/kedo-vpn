from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "tariff", "amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__telegram_id", "payment_id_provider")
    raw_id_fields = ("user", "tariff")

    def has_add_permission(self, request):
        return False
