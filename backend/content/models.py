# backend/content/models.py
from django.db import models


class SiteSettings(models.Model):
    support_link = models.URLField(
        max_length=200,
        verbose_name="Ссылка на поддержку",
        help_text="URL-адрес для кнопки 'Поддержка' в главном меню бота.",
        default="https://t.me/your_support_username",
    )

    def __str__(self):
        return "Тех. поддержка"

    class Meta:
        verbose_name = "Тех. поддержка"
        verbose_name_plural = "Тех. поддержка"


class BroadcastSettings(models.Model):
    broadcast_admin = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Администратор для рассылок (id)",
        help_text="Пользователь, который будет подтверждать или отклонять рассылки. Если не указан, рассылки не работают.",
    )

    def __str__(self):
        return "Админ для рассылок"

    class Meta:
        verbose_name = "Админ для рассылок"
        verbose_name_plural = "Админ для рассылок"
