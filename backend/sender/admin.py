from django.contrib import admin, messages
from django.db import transaction

from .models import Broadcast, SentBroadcastMessage
from .tasks import send_broadcast_for_approval_task


@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "short_text",
        "created_at",
        "status",
        "media_type",
    )
    list_filter = ("status", "media_type", "created_at")
    search_fields = ("text",)
    ordering = ("-created_at",)
    readonly_fields = ("status",)
    fieldsets = (
        (
            "Содержимое рассылки",
            {
                "fields": ("text", ("media_file", "media_type")),
                "description": "Заполните текст и, при необходимости, прикрепите медиафайл. После сохранения рассылка отправится на подтверждение администратору.",
            },
        ),
        (
            "Статус",
            {
                "fields": ("status",),
                "classes": ("collapse",),
            },
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status != Broadcast.Status.PENDING_APPROVAL:
            return [f.name for f in self.model._meta.fields if f.name != "id"]
        return self.readonly_fields

    def save_model(self, request, obj: Broadcast, form, change):
        if obj.media_file and not obj.media_type:
            messages.error(
                request, "Если вы загрузили файл, необходимо указать его тип."
            )
            return
        is_new = not obj.pk
        if is_new:
            obj.status = Broadcast.Status.PENDING_APPROVAL
            super().save_model(request, obj, form, change)
            transaction.on_commit(
                lambda: send_broadcast_for_approval_task.delay(obj.id)
            )
            self.message_user(
                request,
                "Рассылка создана и отправлена на подтверждение администратору.",
                messages.SUCCESS,
            )
        else:
            super().save_model(request, obj, form, change)

    @admin.display(description="Текст", ordering="text")
    def short_text(self, obj: Broadcast):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status == Broadcast.Status.SENT:
            return False
        return True


@admin.register(SentBroadcastMessage)
class SentBroadcastMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "broadcast", "user", "message_id", "sent_at")
    list_filter = ("sent_at",)
    search_fields = ("user__telegram_id", "user__username")
    readonly_fields = [f.name for f in SentBroadcastMessage._meta.fields]

    def has_add_permission(self, request):
        return False
