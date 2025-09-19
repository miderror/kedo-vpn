from django.contrib import admin

from .models import ReferralBonus, ReferralTier


@admin.register(ReferralTier)
class ReferralTierAdmin(admin.ModelAdmin):
    list_display = ("name", "min_payment_amount", "bonus_days", "is_active")
    list_editable = ("is_active",)


@admin.register(ReferralBonus)
class ReferralBonusAdmin(admin.ModelAdmin):
    list_display = ("referrer", "referral", "bonus_days_awarded", "awarded_at")
    list_filter = ("awarded_at",)
    search_fields = (
        "referrer__username",
        "referrer__telegram_id",
        "referral__username",
        "referral__telegram_id",
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [field.name for field in self.model._meta.fields]
        return []

    def has_add_permission(self, request):
        return False
