from datetime import timedelta

from django.db import models
from django.utils import timezone


class Broadcast(models.Model):
    class Status(models.TextChoices):
        PENDING_APPROVAL = "PENDING", "Ожидает подтверждения"
        APPROVED = "APPROVED", "Одобрено (в процессе)"
        SENT = "SENT", "Отправлено"
        CANCELED = "CANCELED", "Отклонено"
        ERROR = "ERROR", "Ошибка"

    class MediaType(models.TextChoices):
        PHOTO = "PHOTO", "Фото"
        VIDEO = "VIDEO", "Видео"
        DOCUMENT = "DOCUMENT", "Документ"
        AUDIO = "AUDIO", "Аудио"

    text = models.TextField(
        verbose_name="Текст сообщения",
        help_text="Основной текст рассылки. Будет отправлен как есть или как подпись к медиафайлу.",
    )
    media_file = models.FileField(
        upload_to="broadcasts/",
        blank=True,
        null=True,
        verbose_name="Медиафайл",
        help_text="Опциональный файл для отправки (фото, видео, документ, аудио).",
    )
    media_type = models.CharField(
        max_length=10,
        choices=MediaType.choices,
        blank=True,
        null=True,
        verbose_name="Тип медиафайла",
        help_text="Необходимо указать тип, если вы прикрепили медиафайл.",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING_APPROVAL,
        verbose_name="Статус",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Рассылка от {self.created_at.strftime('%Y-%m-%d %H:%M')} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["-created_at"]


class SentBroadcastMessage(models.Model):
    broadcast = models.ForeignKey(
        Broadcast, on_delete=models.CASCADE, related_name="sent_messages"
    )
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="broadcast_messages"
    )
    message_id = models.BigIntegerField(verbose_name="ID сообщения в Telegram")
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Время отправки")

    def is_deletable(self):
        return timezone.now() > self.sent_at + timedelta(hours=24)

    def __str__(self):
        return f"Сообщение {self.message_id} для {self.user} из рассылки {self.broadcast.id}"

    class Meta:
        verbose_name = "Отправленное сообщение рассылки"
        verbose_name_plural = "Отправленные сообщения рассылки"
        unique_together = ("user", "message_id")
