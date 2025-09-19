from django.contrib import admin

from .models import NotificationRule, SentNotification


@admin.register(NotificationRule)
class NotificationRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "trigger_hours_before_expiry", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name", "message_template")


@admin.register(SentNotification)
class SentNotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "rule", "sent_at", "subscription_end_date_at_send_time")
    list_filter = ("sent_at", "rule")
    search_fields = ("user__telegram_id", "user__username")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
