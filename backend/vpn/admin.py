from django.contrib import admin
from django.db.models import Sum

from backend.payments.models import Payment
from backend.referrals.models import ReferralBonus

from .models import Subscription, Tariff


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ("name", "duration_days", "price", "is_active", "order")
    list_editable = ("is_active", "order")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "purchased_subscription_days",
        "total_paid",
        "bonus_subscription_days",
    )
    search_fields = ("user__telegram_id", "user__username")
    list_filter = ("end_date", "trial_activated")
    readonly_fields = ("vless_uuid",)

    @admin.display(boolean=True, description="Активна")
    def is_active(self, obj):
        return obj.is_active

    @admin.display(description="Купленная подписка")
    def purchased_subscription_days(self, obj: Subscription) -> int:
        result = Payment.objects.filter(
            user=obj.user, status=Payment.Status.SUCCEEDED
        ).aggregate(total_days=Sum("tariff__duration_days"))
        return result["total_days"] or 0

    @admin.display(description="Бонусная подписка")
    def bonus_subscription_days(self, obj: Subscription) -> int:
        result = ReferralBonus.objects.filter(referrer=obj.user).aggregate(
            total_days=Sum("bonus_days_awarded")
        )
        return result["total_days"] or 0
